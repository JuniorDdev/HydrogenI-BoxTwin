import json
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from urllib import parse, request

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
    def __init__(self, config, database):
        self.config, self.database = config, database
        self.last_sent = {}

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
            for target in targets:
                if int(target.get("escalation_minutes", 0)) > 0:
                    continue  # processado pelo escalonador periódico
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
        self.database.log_notification(anomaly["id"], channel, status, detail, provider_id, target.get("recipient_id"))
        return {"anomaly_id": anomaly["id"], "channel": channel, "status": status}

    def _legacy_targets(self):
        return [{"channel": "email", "email": self.config["ALERT_EMAIL_TO"], "escalation_minutes": 0}, {"channel": "twilio", "phone": self.config["TWILIO_TO"], "escalation_minutes": 0}]

    def _email(self, anomaly, target):
        cfg = self.config
        destination = target.get("email") or cfg["ALERT_EMAIL_TO"]
        if not all((cfg["SMTP_HOST"], cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"], destination)):
            raise RuntimeError("Configuração SMTP incompleta.")
        msg = EmailMessage()
        msg["Subject"] = f"[BoxTwin] Anomalia {anomaly['type']}"
        msg["From"], msg["To"] = cfg["SMTP_USERNAME"], destination
        link = f"{cfg['PUBLIC_BASE_URL']}/admin/anomalies/{anomaly['id']}"
        msg.set_content(f"{anomaly['message']}\nSeveridade: {anomaly['level']}\nData: {anomaly['created_at']}\nAcompanhar: {link}")
        with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=10) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"])
            smtp.send_message(msg)
        return None

    def _twilio(self, anomaly, target):
        cfg = self.config
        destination = target.get("phone") or cfg["TWILIO_TO"]
        if not all((cfg["TWILIO_ACCOUNT_SID"], cfg["TWILIO_AUTH_TOKEN"], cfg["TWILIO_FROM"], destination)):
            raise RuntimeError("Configuração Twilio incompleta.")
        endpoint = f"https://api.twilio.com/2010-04-01/Accounts/{cfg['TWILIO_ACCOUNT_SID']}/Messages.json"
        link = f"{cfg['PUBLIC_BASE_URL']}/admin/anomalies/{anomaly['id']}"
        payload = parse.urlencode({"From": cfg["TWILIO_FROM"], "To": destination, "Body": f"⚠ BoxTwin #{anomaly['id']}: {anomaly['message']}\nResponda '1 {anomaly['id']}' para ciência ou '2 {anomaly['id']}' para atendimento.\n{link}", "StatusCallback": f"{cfg['PUBLIC_BASE_URL']}/api/webhooks/twilio/status"}).encode()
        req = request.Request(endpoint, data=payload)
        token = __import__("base64").b64encode(f"{cfg['TWILIO_ACCOUNT_SID']}:{cfg['TWILIO_AUTH_TOKEN']}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
        with request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode()).get("sid")


class RagService:
    """RAG local simples: recupera procedimentos relevantes e gera tratativa rastreável."""
    def __init__(self, knowledge_path):
        self.documents = json.loads(Path(knowledge_path).read_text(encoding="utf-8"))

    @staticmethod
    def _tokens(text):
        return {word.strip(".,:;!?()[]").lower() for word in text.split() if len(word) > 2}

    def retrieve(self, question, context=None):
        query = self._tokens(question + " " + json.dumps(context or {}, ensure_ascii=False))
        ranked = []
        for doc in self.documents:
            haystack = self._tokens(" ".join((doc["title"], doc["content"], " ".join(doc.get("tags", [])))))
            ranked.append((len(query & haystack), doc))
        sources = [doc for score, doc in sorted(ranked, key=lambda item: item[0], reverse=True) if score > 0][:3]
        return sources

    def answer(self, question, context=None):
        sources = self.retrieve(question, context)
        if not sources:
            return {"answer": "Não encontrei um procedimento correspondente. Encaminhe a anomalia a um responsável técnico.", "sources": [], "mode": "local-rag"}
        steps = sources[0]["content"]
        return {"answer": f"Tratativa sugerida: {steps}", "sources": [{"id": d["id"], "title": d["title"]} for d in sources], "mode": "local-rag"}


class GrokService:
    def __init__(self, config, rag):
        self.config, self.rag = config, rag

    def answer(self, question, context=None):
        sources = self.rag.retrieve(question, context)
        if not self.config["XAI_ENABLED"] or not self.config["XAI_API_KEY"]:
            return self.rag.answer(question, context)
        references = "\n".join(f"[{d['id']}] {d['title']}: {d['content']}" for d in sources)
        system = "Você é o assistente técnico do HydrogenI BoxTwin. Responda em português, use somente os procedimentos fornecidos, cite seus IDs, não invente ações e exija confirmação humana para decisões operacionais."
        prompt = f"Pergunta: {question}\nDados da anomalia: {json.dumps(context or {}, ensure_ascii=False)}\nProcedimentos:\n{references or 'Nenhum procedimento recuperado.'}"
        payload = json.dumps({"model": self.config["XAI_MODEL"], "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]}).encode()
        req = request.Request(f"{self.config['XAI_BASE_URL']}/chat/completions", data=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.config['XAI_API_KEY']}"})
        try:
            with request.urlopen(req, timeout=self.config["XAI_TIMEOUT_SECONDS"]) as response:
                result = json.loads(response.read().decode())
            return {"answer": result["choices"][0]["message"]["content"], "sources": [{"id": d["id"], "title": d["title"]} for d in sources], "mode": "grok-rag"}
        except Exception as exc:
            fallback = self.rag.answer(question, context)
            fallback["fallback_reason"] = str(exc)[:160]
            return fallback
