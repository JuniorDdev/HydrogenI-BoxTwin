import json
from datetime import datetime, timezone
from pathlib import Path
from urllib import parse, request, error as urlerror

import numpy as np


class CalibrationService:
    def __init__(self, path):
        self.path = Path(path)

    def save(self, distance_grid_mm):
        payload = {"version": 1, "empty_distance_grid_mm": distance_grid_mm}
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def load(self):
        if not self.path.exists():
            return None
        return json.loads(self.path.read_text(encoding="utf-8"))["empty_distance_grid_mm"]


class VolumeService:
    def __init__(self, length_m, width_m, height_m):
        self.length_m = length_m
        self.width_m = width_m
        self.height_m = height_m
        self.capacity_m3 = length_m * width_m * height_m
        self.cell_area_m2 = (length_m * width_m) / 64

    def calculate(self, empty_grid_mm, current_grid_mm):
        empty = np.array(empty_grid_mm, dtype=float)
        current = np.array([[np.nan if value is None else value for value in row] for row in current_grid_mm])
        if empty.shape != (8, 8) or current.shape != (8, 8):
            raise ValueError("A leitura deve conter uma matriz 8x8.")
        heights = np.clip((empty - current) / 1000, 0, self.height_m)
        valid = np.isfinite(heights)
        valid_zones = int(valid.sum())
        volume_m3 = float(np.nansum(heights) * self.cell_area_m2)
        capacity_percent = (volume_m3 / self.capacity_m3 * 100) if self.capacity_m3 else 0
        coverage = valid_zones / 64
        confidence_percent = round(coverage * 100, 1)
        safe_heights = np.where(valid, heights, 0).round(4).tolist()
        return {
            "volume_m3": round(volume_m3, 5),
            "capacity_m3": round(self.capacity_m3, 5),
            "capacity_percent": round(capacity_percent, 1),
            "average_height_m": round(float(np.nanmean(heights)) if valid_zones else 0, 4),
            "maximum_height_m": round(float(np.nanmax(heights)) if valid_zones else 0, 4),
            "confidence_percent": confidence_percent,
            "valid_zones": valid_zones,
            "height_grid_m": safe_heights,
        }


class AlertService:
    def __init__(self, capacity_limit, confidence_min):
        self.capacity_limit = capacity_limit
        self.confidence_min = confidence_min

    def evaluate(self, metrics):
        alerts = []
        if metrics["capacity_percent"] >= self.capacity_limit:
            alerts.append({"type": "capacity", "level": "warning", "message": "Capacidade próxima do limite."})
        if metrics["confidence_percent"] < self.confidence_min:
            alerts.append({"type": "confidence", "level": "danger", "message": "Confiança baixa; verificar sensor."})
        if metrics["valid_zones"] < 48:
            alerts.append({"type": "obstruction", "level": "danger", "message": "Possível obstrução ou perda de zonas."})
        return alerts


class NotificationService:
    """Adaptadores opcionais. Falhas externas nunca interrompem a medição."""
    def __init__(self, config, database, rag=None):
        self.config, self.database, self.rag = config, database, rag
        self.last_sent = {}

    def _guidance_for(self, anomaly):
        """Pré-análise e orientação de solução, a partir da mesma base de procedimentos usada pelo
        assistente técnico — inclusa no corpo do e-mail para o destinatário já receber um próximo
        passo, sem precisar abrir o painel."""
        if not self.rag:
            return "Consulte o procedimento técnico correspondente no painel administrativo."
        sources = self.rag.retrieve(anomaly.get("message", ""), context={"type": anomaly.get("type")})
        if not sources:
            return "Nenhum procedimento específico foi encontrado; isole a ocorrência, registre evidências e acione um responsável técnico."
        return sources[0]["content"]

    def dispatch(self, anomalies):
        results = []
        for anomaly in anomalies:
            key = anomaly["type"]
            now = datetime.now(timezone.utc).timestamp()
            if now - self.last_sent.get(key, 0) < self.config["NOTIFY_COOLDOWN_SECONDS"]:
                continue
            self.last_sent[key] = now
            rules = self.database.matching_rules(anomaly)
            targets = rules or self._legacy_targets()
            sent_targets = set()
            for target in targets:
                if int(target.get("escalation_minutes", 0)) > 0:
                    continue  # processado pelo escalonador periódico
                target_key = (
                    target.get("channel"),
                    target.get("email") or self.config["ALERT_EMAIL_TO"],
                    target.get("phone") or self.config["TWILIO_TO"],
                )
                if target_key in sent_targets:
                    continue
                sent_targets.add(target_key)
                result = self._send(anomaly, target)
                if result:
                    results.append(result)
        return results

    def dispatch_escalations(self):
        return [result for anomaly, target in self.database.due_escalations() if (result := self._send(anomaly, target))]

    def _send(self, anomaly, target):
        channel = target["channel"]
        enabled = self.config["EMAIL_ENABLED"] if channel == "email" else self.config["TWILIO_ENABLED"]
        if not enabled:
            return None
        try:
            provider_id = self._email(anomaly, target) if channel == "email" else self._twilio(anomaly, target)
            status, detail = "sent", f"Notificação enviada para {target.get('recipient_name', 'destinatário')}"
        except Exception as exc:
            status, detail, provider_id = "failed", str(exc)[:300], None
        safe_recipient = target.get("recipient_name") or "destinatário configurado"
        print(
            f"[BoxTwin][Notification] channel={channel} status={status} "
            f"recipient={safe_recipient!r} detail={detail}",
            flush=True,
        )
        self.database.log_notification(anomaly["id"], channel, status, detail, provider_id, target.get("recipient_id"))
        return {"anomaly_id": anomaly["id"], "channel": channel, "status": status}

    def _legacy_targets(self):
        return [{"channel": "email", "email": self.config["ALERT_EMAIL_TO"], "escalation_minutes": 0}, {"channel": "twilio", "phone": self.config["TWILIO_TO"], "escalation_minutes": 0}]

    def _email(self, anomaly, target):
        cfg = self.config
        destination = target.get("email") or cfg["ALERT_EMAIL_TO"]
        if not all((cfg["RESEND_API_KEY"], cfg["RESEND_FROM_EMAIL"], destination)):
            raise RuntimeError("Configuração Resend incompleta.")
        link = f"{cfg['PUBLIC_BASE_URL']}/admin/anomalies/{anomaly['id']}"
        guidance = self._guidance_for(anomaly)
        text = (
            f"{anomaly['message']}\n"
            f"Severidade: {anomaly['level']}\n"
            f"Data: {anomaly['created_at']}\n\n"
            f"Pré-análise e orientação de solução:\n{guidance}\n\n"
            f"Acompanhar: {link}"
        )
        payload = json.dumps({
            "from": cfg["RESEND_FROM_EMAIL"],
            "to": [destination],
            "subject": f"[BoxTwin] Anomalia {anomaly['type']}",
            "text": text,
        }).encode()
        req = request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {cfg['RESEND_API_KEY']}",
                # Sem um User-Agent explicito, a Cloudflare na frente da API da Resend bloqueia a
                # requisicao (error code: 1010) por parecer trafego de bot vindo do urllib padrao.
                "User-Agent": "HydrogenI-BoxTwin/1.0 (+https://github.com/JuniorDdev/HydrogenI-BoxTwin)",
            },
        )
        try:
            with request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
        except request.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            raise RuntimeError(f"Falha Resend ({exc.code}): {detail}") from exc
        return result.get("id")

    def _twilio(self, anomaly, target):
        cfg = self.config
        destination = target.get("phone") or cfg["TWILIO_TO"]
        if not all((cfg["TWILIO_ACCOUNT_SID"], cfg["TWILIO_AUTH_TOKEN"], cfg["TWILIO_FROM"], destination)):
            raise RuntimeError("Configuração Twilio incompleta.")
        endpoint = f"https://api.twilio.com/2010-04-01/Accounts/{cfg['TWILIO_ACCOUNT_SID']}/Messages.json"
        link = f"{cfg['PUBLIC_BASE_URL']}/admin/anomalies/{anomaly['id']}"
        message_data = {
            "From": cfg["TWILIO_FROM"],
            "To": destination,
            "StatusCallback": f"{cfg['PUBLIC_BASE_URL']}/api/webhooks/twilio/status",
        }
        content_sid = cfg.get("TWILIO_CONTENT_SID", "").strip()
        if content_sid:
            # O template Quick Reply usa {{1}} para o ID e {{2}} para a mensagem.
            # Os botões devem devolver ack_ID, in_progress_ID e resolved_ID.
            message_data.update({
                "ContentSid": content_sid,
                "ContentVariables": json.dumps({
                    "1": str(anomaly["id"]),
                    "2": str(anomaly["message"]),
                }, ensure_ascii=False),
            })
        else:
            # Compatibilidade com ambientes que ainda não configuraram o template.
            message_data["Body"] = (
                f"⚠ BoxTwin #{anomaly['id']}: {anomaly['message']}\n"
                f"Responda 1 para atendido, 2 para em atendimento ou 3 para resolvido.\n{link}"
            )
        payload = parse.urlencode(message_data).encode()
        req = request.Request(endpoint, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        token = __import__("base64").b64encode(f"{cfg['TWILIO_ACCOUNT_SID']}:{cfg['TWILIO_AUTH_TOKEN']}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
        try:
            with request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode()).get("sid")
        except urlerror.HTTPError as exc:
            raw_detail = exc.read().decode(errors="replace")[:500]
            try:
                provider_error = json.loads(raw_detail)
                code = provider_error.get("code")
                message = provider_error.get("message") or raw_detail
                detail = f"código {code}: {message}" if code else message
            except json.JSONDecodeError:
                detail = raw_detail
            raise RuntimeError(f"Falha Twilio ({exc.code}): {detail}") from exc


class EdgeSyncService:
    """Sincroniza leituras persistidas localmente com um endpoint central idempotente."""

    def __init__(self, config, database):
        self.config = config
        self.database = database

    def enabled(self):
        return bool(self.config["EDGE_SYNC_ENABLED"] and self.config["EDGE_SYNC_TARGET_URL"] and self.config["EDGE_SYNC_TOKEN"])

    def enqueue(self, reading_id, payload):
        if not self.config["EDGE_SYNC_TARGET_URL"]:
            return
        self.database.enqueue_sync(
            reading_id,
            payload["reading_uuid"],
            payload,
            self.config["EDGE_SYNC_TARGET_URL"],
        )

    def process_queue(self):
        if not self.enabled():
            return []
        results = []
        for item in self.database.sync_queue_batch(self.config["EDGE_SYNC_BATCH_SIZE"]):
            self.database.mark_sync_attempt(item["id"])
            try:
                response = self._post_reading(json.loads(item["payload_json"]))
                if not response.get("accepted"):
                    raise RuntimeError(response.get("error") or "Ingestão recusada.")
                self.database.mark_sync_success(item["id"])
                results.append({"reading_uuid": item["reading_uuid"], "status": "synced"})
            except Exception as exc:
                self.database.mark_sync_failure(item["id"], exc)
                results.append({"reading_uuid": item["reading_uuid"], "status": "failed", "error": str(exc)[:200]})
        return results

    def status(self):
        return {
            "enabled": self.enabled(),
            "target_url": self.config["EDGE_SYNC_TARGET_URL"] or None,
            **self.database.sync_status(),
        }

    def push_live_grid(self, payload):
        """Send a diagnostic frame straight to the cloud; it is not a calibrated reading."""
        if not self.enabled():
            return {"status": "disabled"}
        endpoint = f"{self.config['EDGE_SYNC_TARGET_URL'].rstrip('/')}/api/edge/live-grid"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config['EDGE_SYNC_TOKEN']}",
                "User-Agent": "HydrogenI-BoxTwin-LiveGrid/1.0",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.config["EDGE_SYNC_TIMEOUT_SECONDS"]) as response:
                return json.loads(response.read().decode("utf-8"))
        except urlerror.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:400]
            raise RuntimeError(f"Falha ao sincronizar grade ao vivo ({exc.code}): {detail}") from exc

    def _post_reading(self, payload):
        endpoint = f"{self.config['EDGE_SYNC_TARGET_URL'].rstrip('/')}/api/edge/readings"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config['EDGE_SYNC_TOKEN']}",
                "User-Agent": "HydrogenI-BoxTwin-EdgeSync/1.0",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.config["EDGE_SYNC_TIMEOUT_SECONDS"]) as response:
                return json.loads(response.read().decode("utf-8"))
        except urlerror.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:400]
            raise RuntimeError(f"Falha no endpoint central ({exc.code}): {detail}") from exc


class RagService:
    """RAG local simples: recupera procedimentos relevantes e gera tratativa rastreável."""

    # Conectores comuns em PT-BR: sem isso, palavras genéricas (ex.: "com") empatam com termos
    # realmente relevantes (ex.: "obstrução") e desviam o ranking.
    _STOPWORDS = {
        "como", "uma", "uns", "umas", "com", "sem", "para", "por", "dos", "das", "que", "não",
        "mas", "até", "após", "este", "esta", "isso", "essa", "esse", "também", "ainda", "mais",
        "menos", "muito", "pode", "deve", "será", "estão", "está", "seu", "sua", "seus", "suas",
        "quando", "onde", "qual", "quais", "sobre", "entre", "outro", "outra",
    }

    def __init__(self, knowledge_path):
        self.documents = json.loads(Path(knowledge_path).read_text(encoding="utf-8"))

    @classmethod
    def _tokens(cls, text):
        words = (word.strip(".,:;!?()[]").lower() for word in text.split())
        return {word for word in words if len(word) > 2 and word not in cls._STOPWORDS}

    @staticmethod
    def _history_text(history):
        return " ".join(f"{turn.get('question', '')} {turn.get('answer', '')}" for turn in (history or []))

    def retrieve(self, question, context=None, history=None):
        # A pergunta (+ histórico) precisa pesar mais que o contexto da leitura: caso contrário, uma
        # anomalia aberta cujo texto (ex.: "Capacidade próxima do limite") ecoa quase literalmente o
        # título de um procedimento passa a vencer qualquer pergunta, mesmo sem relação com o assunto.
        question_tokens = self._tokens(f"{question} {self._history_text(history)}")
        context_tokens = self._tokens(json.dumps(context or {}, ensure_ascii=False))
        ranked = []
        for doc in self.documents:
            haystack = self._tokens(" ".join((doc["title"], doc["content"], " ".join(doc.get("tags", [])))))
            score = (len(question_tokens & haystack), len(context_tokens & haystack))
            ranked.append((score, doc))
        sources = [doc for score, doc in sorted(ranked, key=lambda item: item[0], reverse=True) if any(score)][:3]
        return sources

    def answer(self, question, context=None, history=None):
        sources = self.retrieve(question, context, history)
        if not sources:
            return {"answer": "Olá. No momento não encontrei um procedimento bem aderente ao caso. Minha orientação mais segura é isolar a ocorrência, registrar a evidência e encaminhar para um responsável técnico validar a próxima ação.", "sources": [], "mode": "local-rag"}
        steps = sources[0]["content"]
        return {
            "answer": f"Olá. Pela ocorrência descrita, a tratativa mais adequada agora é a seguinte: {steps} Depois disso, vale confirmar uma nova leitura e registrar o que foi observado para manter a rastreabilidade da operação.",
            "sources": [{"id": d["id"], "title": d["title"]} for d in sources],
            "mode": "local-rag",
        }


class GroqService:
    """Encaminha a pergunta ao GroqCloud (API compatível com OpenAI); cai para o RAG local se
    desabilitado, sem chave ou em caso de falha."""
    def __init__(self, config, rag):
        self.config, self.rag = config, rag

    def answer(self, question, context=None, history=None):
        sources = self.rag.retrieve(question, context, history)
        if not self.config["GROQ_ENABLED"] or not self.config["GROQ_API_KEY"]:
            return self.rag.answer(question, context, history)
        references = "\n".join(f"[{d['id']}] {d['title']}: {d['content']}" for d in sources)
        system = (
            "Você é o assistente técnico do HydrogenI BoxTwin, falando como um colega experiente orientando um "
            "operador de armazém. Responda em português, em linguagem natural e operacional, do jeito que se "
            "explicaria pessoalmente para alguém no chão de fábrica.\n"
            "Soe humano, educado, sereno e sensato. Quando fizer sentido, comece com uma saudação breve e natural, "
            "sem exagero, e conduza a resposta como apoio prático à decisão.\n"
            "Nunca cite nomes de campos técnicos, chaves de JSON ou de banco de dados (como capacity_percent, "
            "valid_zones, reading_id etc.) — traduza esses dados para termos que o operador entenda (ex.: "
            "'a ocupação está por volta de 92%', nunca 'capacity_percent: 92.3').\n"
            "Use somente os procedimentos fornecidos e cite seus IDs (ex.: PROC-003) como referência das fontes.\n"
            "Você não executa nenhuma ação nem tem acesso ao sistema — só recomenda. Nunca peça confirmação para "
            "agir, nunca diga que vai prosseguir ou executar algo. Termine a resposta orientando o operador a "
            "avaliar e executar conforme sua avaliação operacional, não pedindo permissão para agir.\n"
            "Nunca use formatação markdown de nenhum tipo: sem **negrito**, sem #, ##, ### de títulos, sem "
            "--- ou ___ de divisórias, sem `crase`, sem colchetes/links, sem listas com - ou *. Escreva em texto "
            "corrido normal, com quebras de linha simples separando ideias. Quando precisar listar passos, use "
            "apenas número seguido de ponto e espaço, como '1. Confirme a leitura' — nunca marcadores ou símbolos."
        )
        messages = [{"role": "system", "content": system}]
        for turn in (history or [])[-6:]:
            if turn.get("question"):
                messages.append({"role": "user", "content": str(turn["question"])})
            if turn.get("answer"):
                messages.append({"role": "assistant", "content": str(turn["answer"])})
        prompt = f"Pergunta: {question}\nDados da anomalia: {json.dumps(context or {}, ensure_ascii=False)}\nProcedimentos:\n{references or 'Nenhum procedimento recuperado.'}"
        messages.append({"role": "user", "content": prompt})
        api_key = self.config["GROQ_API_KEY"]
        model = self.config["GROQ_MODEL"]
        payload = json.dumps({"model": model, "messages": messages, "temperature": 0.2}).encode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "BoxTwin3D/1.0",
        }
        # TODO(temporário): remover depois de confirmar o 403 do Groq; mascara a chave no log.
        masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
        print(f"[BoxTwin][Groq] POST https://api.groq.com/openai/v1/chat/completions model={model} "
              f"headers={{'Content-Type': '{headers['Content-Type']}', 'Authorization': 'Bearer {masked_key}', 'User-Agent': '{headers['User-Agent']}'}} "
              f"payload_bytes={len(payload)}")
        req = request.Request("https://api.groq.com/openai/v1/chat/completions", data=payload, headers=headers)
        try:
            with request.urlopen(req, timeout=self.config["GROQ_TIMEOUT_SECONDS"]) as response:
                result = json.loads(response.read().decode())
            return {"answer": result["choices"][0]["message"]["content"], "sources": [{"id": d["id"], "title": d["title"]} for d in sources], "mode": "groq-rag"}
        except urlerror.HTTPError as exc:
            body = exc.read().decode(errors="replace")[:800]
            print(f"[BoxTwin][Groq] HTTP {exc.code} {exc.reason}: {body}")
            fallback = self.rag.answer(question, context, history)
            fallback["fallback_reason"] = f"HTTP {exc.code} {exc.reason}: {body}"[:500]
            return fallback
        except Exception as exc:
            fallback = self.rag.answer(question, context, history)
            fallback["fallback_reason"] = str(exc)[:500]
            return fallback
