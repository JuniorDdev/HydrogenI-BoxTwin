# 🌳 Relatório do Projeto: HydrogenY-BoxTwin

**Diretório Raiz:** `C:/Users/junio/Desktop/PROJETOS PYHTON/HydrogenI - pojeto/HydrogenY-BoxTwin`
**Data da Varredura:** 16/08/2026 00:40:45

## 🏗️ Estrutura de Arquivos

```
📁 HydrogenY-BoxTwin/
├── 📄 app.py
├── 📄 ARQUITETURA_V3.md
├── 📄 DEPLOY_RAILWAY.md
├── 📄 railway.json
├── 📄 README.md
├── 📄 requirements.txt
├── 📄 ROTEIRO_DEMONSTRACAO.md
├── 📁 boxtwin/
│   ├── 📄 config.py
│   ├── 📄 database.py
│   ├── 📄 routes.py
│   ├── 📄 runtime.py
│   ├── 📄 services.py
│   ├── 📄 __init__.py
│   ├── 📁 knowledge/
│   │   ├── 📄 procedures.json
│   ├── 📁 sensors/
│   │   ├── 📄 base.py
│   │   ├── 📄 mock.py
│   │   ├── 📄 vl53l5cx.py
│   │   ├── 📄 vl53l8cx.py
│   │   ├── 📄 __init__.py
│   ├── 📁 static/
│   │   ├── 📄 admin.js
│   │   ├── 📄 anomaly.js
│   │   ├── 📄 app.js
│   │   ├── 📄 service-worker.js
│   │   ├── 📄 style.css
│   ├── 📁 templates/
│   │   ├── 📄 admin.html
│   │   ├── 📄 anomaly.html
│   │   ├── 📄 index.html
│   │   ├── 📄 login.html
├── 📁 data/
│   ├── 📄 calibration.json
├── 📁 HydrogenI_BoxTwin_Railway_Ready_v6/
│   ├── 📄 app.py
│   ├── 📄 ARQUITETURA_V3.md
│   ├── 📄 DEPLOY_RAILWAY.md
│   ├── 📄 railway.json
│   ├── 📄 README.md
│   ├── 📄 requirements.txt
│   ├── 📄 ROTEIRO_DEMONSTRACAO.md
│   ├── 📁 boxtwin/
│   │   ├── 📄 config.py
│   │   ├── 📄 database.py
│   │   ├── 📄 reports.py
│   │   ├── 📄 routes.py
│   │   ├── 📄 runtime.py
│   │   ├── 📄 services.py
│   │   ├── 📄 __init__.py
│   │   ├── 📁 knowledge/
│   │   │   ├── 📄 procedures.json
│   │   ├── 📁 sensors/
│   │   │   ├── 📄 base.py
│   │   │   ├── 📄 mock.py
│   │   │   ├── 📄 vl53l5cx.py
│   │   │   ├── 📄 vl53l8cx.py
│   │   │   ├── 📄 __init__.py
│   │   ├── 📁 static/
│   │   │   ├── 📄 admin.js
│   │   │   ├── 📄 anomaly.js
│   │   │   ├── 📄 app.js
│   │   │   ├── 📄 landing.js
│   │   │   ├── 📄 service-worker.js
│   │   │   ├── 📄 style.css
│   │   ├── 📁 templates/
│   │   │   ├── 📄 admin.html
│   │   │   ├── 📄 anomaly.html
│   │   │   ├── 📄 index.html
│   │   │   ├── 📄 login.html
│   │   │   ├── 📄 simulator.html
│   ├── 📁 data/
│   ├── 📁 output/
│   │   ├── 📁 pdf/
│   ├── 📁 systemd/
│   ├── 📁 tests/
│   │   ├── 📄 test_admin.py
│   │   ├── 📄 test_api.py
│   │   ├── 📄 test_volume.py
├── 📁 systemd/
├── 📁 tests/
│   ├── 📄 test_admin.py
│   ├── 📄 test_api.py
│   ├── 📄 test_volume.py
```


---

## 📜 Conteúdo dos Arquivos

### 📄 `app.py`

```python
from boxtwin import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host=app.config["APP_HOST"], port=app.config["APP_PORT"], debug=app.config["APP_DEBUG"])


```

### 📄 `ARQUITETURA_V3.md`

```markdown
# Arquitetura BoxTwin v3

## Fluxo operacional

1. O sensor real ou simulado produz uma matriz 8×8.
2. O serviço de volume calcula ocupação, altura, confiança e zonas válidas.
3. O motor de regras identifica capacidade alta, baixa confiança e obstrução.
4. A leitura e as anomalias são gravadas no SQLite.
5. O painel recebe a nova leitura por SSE (`GET /api/stream`).
6. Adaptadores opcionais enviam e-mail ou Twilio com intervalo antirrepetição.
7. O administrador registra ciência e consulta a tratativa no RAG local.

## API preparada para Flutter

| Método | Rota | Uso |
|---|---|---|
| GET | `/api/health` | estado e dimensões do BoxNode |
| GET | `/api/readings/latest` | leitura mais recente |
| GET | `/api/readings/history` | série histórica |
| GET | `/api/stream` | eventos em tempo real |
| GET | `/api/admin/anomalies` | fila protegida de incidentes |
| POST | `/api/admin/anomalies/{id}/acknowledge` | registro de ciência |
| POST | `/api/admin/assistant` | consulta ao RAG |

Para o aplicativo Flutter, a etapa seguinte deverá substituir a sessão web nas rotas móveis por JWT de curta duração, HTTPS obrigatório e armazenamento seguro do token. Não exponha diretamente o Raspberry Pi na internet; utilize um backend central ou VPN/túnel autenticado.

## IA e RAG

A base inicial fica em `boxtwin/knowledge/procedures.json`. O serviço recupera documentos por relevância lexical e devolve as fontes utilizadas. Essa abordagem funciona offline e é adequada ao MVP. Na evolução, o mesmo contrato pode usar embeddings, um banco vetorial e um modelo de linguagem; mantenha sempre as fontes, os limites de decisão e a aprovação humana para ações operacionais.

Quando `XAI_ENABLED=true`, o Grok recebe a pergunta, os dados técnicos da anomalia e somente os procedimentos recuperados. Se houver timeout, indisponibilidade ou chave inválida, a resposta volta automaticamente ao modo `local-rag`.

## Respostas pelo Twilio

- `1 42`: registra ciência da anomalia 42;
- `2 42`: marca a anomalia 42 como em atendimento;
- `3 42`: marca a anomalia 42 como resolvida.

Os webhooks validam `X-Twilio-Signature` quando `TWILIO_VALIDATE_SIGNATURE=true`.

## Segurança antes de publicar

- Alterar `ADMIN_PASSWORD` e `SECRET_KEY`.
- Guardar `.env` fora do GitHub.
- Usar HTTPS e cookies seguros em produção.
- Criar usuários individuais e trilha de auditoria na próxima fase.
- Não permitir que a IA acione máquinas ou descarte alertas automaticamente.
- Usar credenciais de teste do Twilio antes de habilitar mensagens reais.

## Validação

```powershell
pip install -r requirements.txt
pytest -q
python app.py
```

Teste em Android na mesma rede acessando `http://IP_DO_COMPUTADOR:5000`. Em produção, utilize HTTPS.

```

### 📄 `DEPLOY_RAILWAY.md`

```markdown
# Deploy do HydrogenI BoxTwin no Railway

## Fonte

- Repositório: `JuniorDdev/HydrogenI-BoxTwin`
- Branch de homologação: `dev/d-junior`
- Health check: `/api/health`
- Processo: Gunicorn, 1 worker e 8 threads

## Volume persistente obrigatório

Conecte um Railway Volume ao serviço com o caminho:

```text
/app/data
```

O Volume preserva o SQLite, a calibração, destinatários, regras, anomalias e histórico entre deployments.

## Variáveis mínimas

```env
SENSOR_MODE=mock
APP_DEBUG=false
ADMIN_USERNAME=admin
ADMIN_PASSWORD=SUBSTITUA_POR_UMA_SENHA_FORTE
SECRET_KEY=SUBSTITUA_POR_UMA_CHAVE_ALEATORIA_LONGA
BOX_NODE_ID=BOX-DEMO-01
BOX_NAME=Box reduzido HydrogenI
BOX_LENGTH_M=0.60
BOX_WIDTH_M=0.40
BOX_HEIGHT_M=0.50
SAMPLE_INTERVAL_SECONDS=15
CAPACITY_ALERT_PERCENT=85
MIN_CONFIDENCE_PERCENT=70
EMAIL_ENABLED=false
TWILIO_ENABLED=false
XAI_ENABLED=false
TWILIO_VALIDATE_SIGNATURE=true
```

Não defina `PORT`; o Railway fornece essa variável automaticamente.

Depois de gerar o domínio público, acrescente:

```env
PUBLIC_BASE_URL=https://SEU-DOMINIO.up.railway.app
```

Ative Grok, Twilio e e-mail separadamente somente depois de validar painel, login, banco e Volume.

## Verificação

```text
https://SEU-DOMINIO/api/health
https://SEU-DOMINIO/
https://SEU-DOMINIO/admin
```

O `manifest.webmanifest` está incluído em `boxtwin/static`, permitindo que o Service Worker conclua o cache inicial da PWA.

```

### 📄 `railway.json`

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120 app:app",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 120,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}

```

### 📄 `README.md`

```markdown
# HydrogenI BoxTwin 3D — MVP demonstrável

Aplicação Flask para demonstrar a medição automatizada do volume de fertilizantes em boxes. Esta versão funciona totalmente sem o sensor físico: um sensor virtual gera uma matriz de profundidade 8×8, e o mesmo fluxo de cálculo usado no modo simulado receberá futuramente as leituras do VL53L8CX.

## O que está pronto

- nove cenários de demonstração: vazio, 25%, 50%, 75%, quase cheio, pilha central, inclinação, carga irregular e obstrução;
- calibração do box vazio;
- matriz de 64 zonas com altura em centímetros;
- cálculo de volume, ocupação, altura média e altura máxima;
- referência conhecida e erro da simulação em pontos percentuais;
- gêmeo digital 3D em Canvas, sem bibliotecas externas;
- histórico local em SQLite;
- alertas de capacidade, confiança e obstrução;
- interface responsiva e operação offline;
- adaptadores separados para modo virtual, VL53L5CX e futuro VL53L8CX.

## Execução no Windows

No terminal do VS Code, dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Acesse `http://127.0.0.1:5000`. Na primeira abertura, o sistema calibra automaticamente o box vazio e apresenta uma pilha central.

Se o PowerShell bloquear a ativação do ambiente, execute uma vez:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Execução no Linux ou Raspberry Pi

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## Como a simulação representa o sensor

O `MockSensor` entrega a mesma estrutura esperada do hardware:

```text
matriz 8×8 de distâncias em milímetros
        ↓
distância do box vazio - distância atual
        ↓
altura da carga em cada célula
        ↓
soma das 64 células × área de cada célula
        ↓
volume total e percentual de ocupação
```

O simulador acrescenta ruído pequeno e determinístico para imitar variação de leitura. O cenário de obstrução retorna zonas inválidas para demonstrar a queda de confiança.

## Configuração da maquete

Edite o arquivo `.env`:

```dotenv
BOX_LENGTH_M=0.60
BOX_WIDTH_M=0.40
BOX_HEIGHT_M=0.50
SENSOR_MODE=mock
```

As três dimensões representam as medidas internas úteis do box. A capacidade é calculada por `comprimento × largura × altura`.

## Integração futura do VL53L8CX

O ponto de integração está em `boxtwin/sensors/vl53l8cx.py`. O adaptador deverá retornar uma lista 8×8 em milímetros e manter `None` nas zonas inválidas. Depois da implementação do driver, altere:

```dotenv
SENSOR_MODE=vl53l8cx
```

O cálculo, banco, API, alertas e painel não precisarão ser reescritos.

## API principal

| Método | Rota | Finalidade |
|---|---|---|
| GET | `/api/health` | Estado do BoxNode e dimensões |
| POST | `/api/demo/setup` | Calibra vazio e inicia a demonstração |
| GET | `/api/demo/scenarios` | Lista cenários disponíveis |
| POST | `/api/demo/scenario/<id>` | Aplica cenário e captura uma leitura |
| POST | `/api/calibration` | Salva a linha de base vazia |
| POST | `/api/readings` | Captura nova leitura |
| GET | `/api/readings/latest` | Retorna a leitura mais recente |
| GET | `/api/readings/history` | Retorna histórico local |

## Testes

```powershell
python -m pytest -q
```

Os testes verificam volume de meia carga, alertas, validação da matriz, inicialização da API, preparação da demonstração e troca de cenários.

## Limite desta versão

Os números no modo `mock` demonstram o método matemático e a experiência operacional, mas não constituem validação de precisão do sensor real. A margem de erro industrial deverá ser medida depois com o VL53L8CX instalado e volumes físicos conhecidos.
# Evolução operacional v3

Além do painel do gêmeo digital, esta versão inclui:

- área administrativa autenticada em `/admin`;
- fila de anomalias com registro de ciência;
- atualização em tempo real via Server-Sent Events (SSE);
- notificações opcionais por SMTP e Twilio (SMS ou WhatsApp Sandbox);
- assistente local com RAG sobre procedimentos em `boxtwin/knowledge/procedures.json`;
- PWA responsiva para Android e contrato JSON reutilizável por um futuro app Flutter.
- cadastro de responsáveis individuais ou equipes;
- regras por anomalia, severidade, canal e tempo de escalonamento;
- Grok pela API da xAI com fallback automático para o RAG local;
- página detalhada de cada incidente, evidências e linha do tempo;
- estados `aberta`, `ciente`, `em atendimento`, `resolvida` e `falso positivo`;
- webhooks Twilio para status de entrega e respostas `1 ID`, `2 ID` ou `3 ID`.

No primeiro acesso local, use `admin` / `HydrogenI@2026` e altere ambos no `.env` antes de qualquer publicação. Para produção, use uma senha forte e uma `SECRET_KEY` aleatória. O RAG atual é deliberadamente local e baseado em recuperação; um provedor de LLM pode ser conectado depois sem mudar a interface administrativa.

Para o Twilio, cadastre os webhooks públicos em `/api/webhooks/twilio/incoming` (mensagens recebidas) e `/api/webhooks/twilio/status` (status). O endereço de `PUBLIC_BASE_URL` deve coincidir exatamente com o domínio HTTPS informado ao Twilio para a validação de assinatura funcionar.

```

### 📄 `requirements.txt`

```
Flask==3.1.1
python-dotenv==1.1.1
numpy==2.2.6
pytest==8.4.1
gunicorn>=23.0,<24.0

```

### 📄 `ROTEIRO_DEMONSTRACAO.md`

```markdown
# Roteiro rápido de demonstração — HydrogenI BoxTwin 3D

## Preparação

1. Execute `python app.py` e abra `http://127.0.0.1:5000`.
2. Clique em **Preparar demonstração**.
3. Deixe aberta a visualização da pilha central.
4. Teste previamente os cenários 50%, irregular, quase cheio e obstrução.

## Demonstração sugerida

1. **Problema:** explique que o estoque atual depende de estimativa visual e atualização manual.
2. **Box vazio:** selecione o cenário vazio e mostre a calibração da referência.
3. **Medição conhecida:** selecione 50% e destaque volume, ocupação e erro contra a referência.
4. **Carga realista:** selecione pilha central ou irregular e mostre por que uma medição em ponto único não representa toda a superfície.
5. **Alerta:** selecione quase cheio e mostre o alerta de capacidade.
6. **Confiabilidade:** selecione obstrução e mostre a redução das zonas válidas.
7. **Evolução:** informe que o sensor virtual será substituído pelo VL53L8CX sem alterar cálculo, banco ou painel.

## Frase de encerramento

“Hoje demonstramos todo o fluxo de decisão com uma matriz virtual 8×8. Com o VL53L8CX, substituímos apenas a origem dos dados e mantemos o mesmo cálculo volumétrico, histórico, alertas e gêmeo digital.”

```

### 📄 `boxtwin\config.py`

```python
import os
from pathlib import Path

from dotenv import load_dotenv


def _bool(name, default=False):
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def load_config():
    load_dotenv()
    root = Path(__file__).resolve().parent.parent
    return {
        "APP_HOST": os.getenv("APP_HOST", "0.0.0.0"),
        "APP_PORT": int(os.getenv("PORT", os.getenv("APP_PORT", "5000"))),
        "APP_DEBUG": _bool("APP_DEBUG"),
        "SENSOR_MODE": os.getenv("SENSOR_MODE", "mock"),
        "BOX_NODE_ID": os.getenv("BOX_NODE_ID", "BOX-DEMO-01"),
        "BOX_NAME": os.getenv("BOX_NAME", "Box reduzido HydrogenI"),
        "BOX_LENGTH_M": float(os.getenv("BOX_LENGTH_M", "0.60")),
        "BOX_WIDTH_M": float(os.getenv("BOX_WIDTH_M", "0.40")),
        "BOX_HEIGHT_M": float(os.getenv("BOX_HEIGHT_M", "0.50")),
        "SAMPLE_INTERVAL_SECONDS": float(os.getenv("SAMPLE_INTERVAL_SECONDS", "5")),
        "CAPACITY_ALERT_PERCENT": float(os.getenv("CAPACITY_ALERT_PERCENT", "85")),
        "MIN_CONFIDENCE_PERCENT": float(os.getenv("MIN_CONFIDENCE_PERCENT", "70")),
        "SECRET_KEY": os.getenv("SECRET_KEY", "troque-esta-chave-no-ambiente"),
        "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME", "admin"),
        "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD", "HydrogenI@2026"),
        "NOTIFY_COOLDOWN_SECONDS": int(os.getenv("NOTIFY_COOLDOWN_SECONDS", "300")),
        "EMAIL_ENABLED": _bool("EMAIL_ENABLED"),
        "SMTP_HOST": os.getenv("SMTP_HOST", ""),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME", ""),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
        "ALERT_EMAIL_TO": os.getenv("ALERT_EMAIL_TO", ""),
        "TWILIO_ENABLED": _bool("TWILIO_ENABLED"),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "TWILIO_FROM": os.getenv("TWILIO_FROM", ""),
        "TWILIO_TO": os.getenv("TWILIO_TO", ""),
        "PUBLIC_BASE_URL": os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:5000").rstrip("/"),
        "XAI_ENABLED": _bool("XAI_ENABLED"),
        "XAI_API_KEY": os.getenv("XAI_API_KEY", ""),
        "XAI_MODEL": os.getenv("XAI_MODEL", "latest"),
        "XAI_BASE_URL": os.getenv("XAI_BASE_URL", "https://api.x.ai/v1").rstrip("/"),
        "XAI_TIMEOUT_SECONDS": int(os.getenv("XAI_TIMEOUT_SECONDS", "20")),
        "TWILIO_VALIDATE_SIGNATURE": _bool("TWILIO_VALIDATE_SIGNATURE", True),
        "DATABASE_PATH": str(root / os.getenv("DATABASE_PATH", "data/boxtwin.db")),
        "CALIBRATION_PATH": str(root / os.getenv("CALIBRATION_PATH", "data/calibration.json")),
    }

```

### 📄 `boxtwin\database.py`

```python
import json
import sqlite3
from datetime import datetime, timezone


class Database:
    def __init__(self, path):
        self.path = path

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    volume_m3 REAL NOT NULL,
                    capacity_percent REAL NOT NULL,
                    confidence_percent REAL NOT NULL,
                    valid_zones INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    alerts_json TEXT NOT NULL,
                    grid_json TEXT NOT NULL,
                    scenario TEXT,
                    reference_percent REAL,
                    reference_error_points REAL,
                    average_height_m REAL,
                    maximum_height_m REAL,
                    capacity_m3 REAL
                )
            """)
            existing = {row[1] for row in connection.execute("PRAGMA table_info(readings)")}
            migrations = {
                "scenario": "TEXT",
                "reference_percent": "REAL",
                "reference_error_points": "REAL",
                "average_height_m": "REAL",
                "maximum_height_m": "REAL",
                "capacity_m3": "REAL",
            }
            for column, column_type in migrations.items():
                if column not in existing:
                    connection.execute(f"ALTER TABLE readings ADD COLUMN {column} {column_type}")
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    reading_id INTEGER,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    acknowledged_at TEXT,
                    resolution_note TEXT
                );
                CREATE TABLE IF NOT EXISTS notification_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    anomaly_id INTEGER,
                    channel TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT,
                    provider_message_id TEXT,
                    delivery_status TEXT,
                    recipient_id INTEGER
                );
                CREATE TABLE IF NOT EXISTS recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    recipient_type TEXT NOT NULL DEFAULT 'administrator',
                    team_name TEXT,
                    email TEXT,
                    phone TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS notification_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL DEFAULT '*',
                    recipient_id INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    escalation_minutes INTEGER NOT NULL DEFAULT 0,
                    active INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY(recipient_id) REFERENCES recipients(id)
                );
                CREATE TABLE IF NOT EXISTS incident_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anomaly_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    note TEXT
                );
            """)
            notification_columns = {row[1] for row in connection.execute("PRAGMA table_info(notification_log)")}
            for column in ("provider_message_id", "delivery_status", "recipient_id"):
                if column not in notification_columns:
                    connection.execute(f"ALTER TABLE notification_log ADD COLUMN {column} {'INTEGER' if column == 'recipient_id' else 'TEXT'}")

    def save_reading(self, reading):
        created_at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute("""
                INSERT INTO readings (
                    created_at, node_id, volume_m3, capacity_percent,
                    confidence_percent, valid_zones, status, alerts_json, grid_json
                    , scenario, reference_percent, reference_error_points,
                    average_height_m, maximum_height_m, capacity_m3
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                created_at, reading["node_id"], reading["volume_m3"], reading["capacity_percent"],
                reading["confidence_percent"], reading["valid_zones"], reading["status"],
                json.dumps(reading["alerts"]), json.dumps(reading["height_grid_m"]),
                reading.get("scenario"), reading.get("reference_percent"),
                reading.get("reference_error_points"), reading.get("average_height_m"),
                reading.get("maximum_height_m"), reading.get("capacity_m3"),
            ))
            return cursor.lastrowid, created_at

    def latest(self):
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1").fetchone()
        return self._serialize(row) if row else None

    def history(self, limit=50):
        limit = max(1, min(int(limit), 500))
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [self._serialize(row) for row in reversed(rows)]

    def save_anomalies(self, reading_id, alerts):
        created_at = datetime.now(timezone.utc).isoformat()
        records = []
        with self.connect() as connection:
            for alert in alerts:
                cursor = connection.execute(
                    "INSERT INTO anomalies (created_at, reading_id, anomaly_type, severity, message) VALUES (?, ?, ?, ?, ?)",
                    (created_at, reading_id, alert["type"], alert["level"], alert["message"]),
                )
                records.append({"id": cursor.lastrowid, "created_at": created_at, **alert, "status": "open"})
        return records

    def anomalies(self, limit=100, status=None):
        query, params = "SELECT * FROM anomalies", []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(max(1, min(int(limit), 500)))
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(query, params).fetchall()]

    def update_anomaly_status(self, anomaly_id, status, note="", actor="Administrador"):
        allowed = {"open", "acknowledged", "in_progress", "resolved", "false_positive"}
        if status not in allowed:
            raise ValueError("Status de anomalia inválido.")
        at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute(
                "UPDATE anomalies SET status=?, acknowledged_at=COALESCE(acknowledged_at, ?), resolution_note=? WHERE id=?",
                (status, at, note, anomaly_id),
            )
            if cursor.rowcount:
                connection.execute(
                    "INSERT INTO incident_events (anomaly_id, created_at, actor, event_type, note) VALUES (?, ?, ?, ?, ?)",
                    (anomaly_id, at, actor, status, note),
                )
        return cursor.rowcount > 0

    def acknowledge_anomaly(self, anomaly_id, note=""):
        return self.update_anomaly_status(anomaly_id, "acknowledged", note)

    def anomaly_detail(self, anomaly_id):
        with self.connect() as connection:
            anomaly = connection.execute("SELECT * FROM anomalies WHERE id=?", (anomaly_id,)).fetchone()
            if not anomaly:
                return None
            reading = connection.execute("SELECT * FROM readings WHERE id=?", (anomaly["reading_id"],)).fetchone()
            events = connection.execute("SELECT * FROM incident_events WHERE anomaly_id=? ORDER BY id", (anomaly_id,)).fetchall()
            notifications = connection.execute("SELECT * FROM notification_log WHERE anomaly_id=? ORDER BY id DESC", (anomaly_id,)).fetchall()
        return {"anomaly": dict(anomaly), "reading": self._serialize(reading) if reading else None, "events": [dict(x) for x in events], "notifications": [dict(x) for x in notifications]}

    def save_recipient(self, payload):
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO recipients (name, recipient_type, team_name, email, phone, active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (payload["name"], payload.get("recipient_type", "administrator"), payload.get("team_name"), payload.get("email"), payload.get("phone"), int(payload.get("active", True)), now),
            )
            return cursor.lastrowid

    def recipients(self):
        with self.connect() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM recipients ORDER BY active DESC, name").fetchall()]

    def save_rule(self, payload):
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO notification_rules (anomaly_type, severity, recipient_id, channel, escalation_minutes, active) VALUES (?, ?, ?, ?, ?, ?)",
                (payload["anomaly_type"], payload.get("severity", "*"), int(payload["recipient_id"]), payload["channel"], max(0, int(payload.get("escalation_minutes", 0))), int(payload.get("active", True))),
            )
            return cursor.lastrowid

    def rules(self):
        with self.connect() as connection:
            rows = connection.execute("SELECT r.*, p.name recipient_name, p.email, p.phone FROM notification_rules r JOIN recipients p ON p.id=r.recipient_id ORDER BY r.id DESC").fetchall()
        return [dict(row) for row in rows]

    def matching_rules(self, anomaly):
        with self.connect() as connection:
            rows = connection.execute("""SELECT r.*, p.name recipient_name, p.email, p.phone
                FROM notification_rules r JOIN recipients p ON p.id=r.recipient_id
                WHERE r.active=1 AND p.active=1 AND (r.anomaly_type=? OR r.anomaly_type='*')
                AND (r.severity=? OR r.severity='*') ORDER BY r.escalation_minutes""",
                (anomaly["type"], anomaly["level"])).fetchall()
        return [dict(row) for row in rows]

    def due_escalations(self):
        now = datetime.now(timezone.utc)
        due = []
        with self.connect() as connection:
            anomalies = connection.execute("SELECT * FROM anomalies WHERE status IN ('open','acknowledged','in_progress')").fetchall()
            for row in anomalies:
                anomaly = dict(row)
                age_minutes = (now - datetime.fromisoformat(anomaly["created_at"])).total_seconds() / 60
                rules = connection.execute("""SELECT r.*, p.name recipient_name, p.email, p.phone
                    FROM notification_rules r JOIN recipients p ON p.id=r.recipient_id
                    WHERE r.active=1 AND p.active=1 AND r.escalation_minutes>0
                    AND (r.anomaly_type=? OR r.anomaly_type='*') AND (r.severity=? OR r.severity='*')""",
                    (anomaly["anomaly_type"], anomaly["severity"])).fetchall()
                for rule_row in rules:
                    rule = dict(rule_row)
                    already = connection.execute("SELECT 1 FROM notification_log WHERE anomaly_id=? AND recipient_id=? AND channel=?", (anomaly["id"], rule["recipient_id"], rule["channel"])).fetchone()
                    if age_minutes >= rule["escalation_minutes"] and not already:
                        due.append(({"id": anomaly["id"], "type": anomaly["anomaly_type"], "level": anomaly["severity"], "message": anomaly["message"], "created_at": anomaly["created_at"]}, rule))
        return due

    def log_notification(self, anomaly_id, channel, status, detail="", provider_message_id=None, recipient_id=None):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO notification_log (created_at, anomaly_id, channel, status, detail, provider_message_id, delivery_status, recipient_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), anomaly_id, channel, status, detail, provider_message_id, status, recipient_id),
            )

    def update_delivery_status(self, provider_message_id, status, detail=""):
        with self.connect() as connection:
            cursor = connection.execute("UPDATE notification_log SET delivery_status=?, detail=COALESCE(NULLIF(?,''), detail) WHERE provider_message_id=?", (status, detail, provider_message_id))
        return cursor.rowcount

    def notification_history(self, limit=100):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM notification_log ORDER BY id DESC LIMIT ?", (max(1, min(int(limit), 500)),)
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _serialize(row):
        return {
            "id": row["id"], "created_at": row["created_at"], "node_id": row["node_id"],
            "volume_m3": row["volume_m3"], "capacity_percent": row["capacity_percent"],
            "confidence_percent": row["confidence_percent"], "valid_zones": row["valid_zones"],
            "status": row["status"], "alerts": json.loads(row["alerts_json"]),
            "height_grid_m": json.loads(row["grid_json"]),
            "scenario": row["scenario"], "reference_percent": row["reference_percent"],
            "reference_error_points": row["reference_error_points"],
            "average_height_m": row["average_height_m"],
            "maximum_height_m": row["maximum_height_m"], "capacity_m3": row["capacity_m3"],
        }

```

### 📄 `boxtwin\routes.py`

```python
import json
import time
import base64
import hashlib
import hmac
from functools import wraps

from flask import Blueprint, Response, current_app, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("main", __name__)


def runtime():
    return current_app.extensions["boxtwin_runtime"]


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Autenticação administrativa necessária."}), 401
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


@bp.get("/")
def dashboard():
    return render_template("index.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        expected = current_app.config["ADMIN_PASSWORD"]
        password_ok = check_password_hash(expected, password) if expected.startswith(("pbkdf2:", "scrypt:")) else password == expected
        if username == current_app.config["ADMIN_USERNAME"] and password_ok:
            session.clear()
            session["admin_authenticated"] = True
            return redirect(url_for("main.admin"))
        error = "Usuário ou senha inválidos."
    return render_template("login.html", error=error)


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.get("/admin")
@admin_required
def admin():
    return render_template("admin.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/admin/anomalies/<int:anomaly_id>")
@admin_required
def anomaly_page(anomaly_id):
    if not runtime().database.anomaly_detail(anomaly_id):
        return "Anomalia não encontrada.", 404
    return render_template("anomaly.html", anomaly_id=anomaly_id)


@bp.get("/api/health")
def health():
    volume = runtime().volume
    return jsonify({
        "status": "online",
        "node_id": current_app.config["BOX_NODE_ID"],
        "box_name": current_app.config["BOX_NAME"],
        "sensor_mode": current_app.config["SENSOR_MODE"],
        "demo_enabled": hasattr(runtime().sensor, "set_scenario"),
        "dimensions_m": {
            "length": volume.length_m,
            "width": volume.width_m,
            "height": volume.height_m,
        },
        "capacity_m3": volume.capacity_m3,
    })


@bp.post("/api/calibration")
def calibrate():
    return jsonify(runtime().calibrate())


@bp.post("/api/readings")
def capture():
    result = runtime().capture()
    return jsonify(result), 409 if result.get("status") == "not_calibrated" else 201


@bp.get("/api/readings/latest")
def latest():
    return jsonify(runtime().database.latest() or {"status": "no_data"})


@bp.get("/api/readings/history")
def history():
    return jsonify(runtime().database.history(request.args.get("limit", 50)))


@bp.get("/api/stream")
def stream():
    def events():
        last_id = None
        while True:
            reading = runtime().database.latest()
            if reading and reading["id"] != last_id:
                last_id = reading["id"]
                yield f"event: reading\ndata: {json.dumps(reading)}\n\n"
            else:
                yield ": keep-alive\n\n"
            time.sleep(2)
    return Response(events(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@bp.get("/api/admin/anomalies")
@admin_required
def anomalies():
    return jsonify(runtime().database.anomalies(request.args.get("limit", 100), request.args.get("status")))


@bp.post("/api/admin/anomalies/<int:anomaly_id>/acknowledge")
@admin_required
def acknowledge(anomaly_id):
    payload = request.get_json(silent=True) or {}
    if not runtime().database.acknowledge_anomaly(anomaly_id, payload.get("note", "")):
        return jsonify({"error": "Anomalia não encontrada."}), 404
    return jsonify({"ok": True, "id": anomaly_id})


@bp.get("/api/admin/anomalies/<int:anomaly_id>")
@admin_required
def anomaly_detail(anomaly_id):
    detail = runtime().database.anomaly_detail(anomaly_id)
    return (jsonify(detail), 200) if detail else (jsonify({"error": "Anomalia não encontrada."}), 404)


@bp.post("/api/admin/anomalies/<int:anomaly_id>/status")
@admin_required
def anomaly_status(anomaly_id):
    payload = request.get_json(silent=True) or {}
    try:
        found = runtime().database.update_anomaly_status(anomaly_id, payload.get("status", ""), payload.get("note", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return (jsonify({"ok": True}), 200) if found else (jsonify({"error": "Anomalia não encontrada."}), 404)


@bp.route("/api/admin/recipients", methods=["GET", "POST"])
@admin_required
def recipients():
    if request.method == "GET":
        return jsonify(runtime().database.recipients())
    payload = request.get_json(silent=True) or {}
    if not str(payload.get("name", "")).strip() or (not payload.get("email") and not payload.get("phone")):
        return jsonify({"error": "Informe nome e ao menos e-mail ou telefone."}), 400
    return jsonify({"id": runtime().database.save_recipient(payload)}), 201


@bp.route("/api/admin/rules", methods=["GET", "POST"])
@admin_required
def rules():
    if request.method == "GET":
        return jsonify(runtime().database.rules())
    payload = request.get_json(silent=True) or {}
    if payload.get("channel") not in {"email", "twilio"} or not payload.get("recipient_id"):
        return jsonify({"error": "Destinatário e canal válido são obrigatórios."}), 400
    payload.setdefault("anomaly_type", "*")
    return jsonify({"id": runtime().database.save_rule(payload)}), 201


@bp.get("/api/admin/notifications")
@admin_required
def notifications():
    return jsonify(runtime().database.notification_history(request.args.get("limit", 100)))


@bp.post("/api/admin/assistant")
@admin_required
def assistant():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"error": "Informe uma pergunta."}), 400
    return jsonify(runtime().assistant.answer(question, payload.get("context")))


def valid_twilio_signature():
    if not current_app.config["TWILIO_VALIDATE_SIGNATURE"]:
        return True
    signature = request.headers.get("X-Twilio-Signature", "")
    token = current_app.config["TWILIO_AUTH_TOKEN"]
    if not signature or not token:
        return False
    public_url = current_app.config["PUBLIC_BASE_URL"] + request.path
    material = public_url + "".join(key + value for key in sorted(request.form) for value in request.form.getlist(key))
    expected = base64.b64encode(hmac.new(token.encode(), material.encode(), hashlib.sha1).digest()).decode()
    return hmac.compare_digest(signature, expected)


@bp.post("/api/webhooks/twilio/status")
def twilio_status():
    if not valid_twilio_signature():
        return "Invalid signature", 403
    sid, status = request.form.get("MessageSid", ""), request.form.get("MessageStatus", "")
    runtime().database.update_delivery_status(sid, status, request.form.get("ErrorMessage", ""))
    return "", 204


@bp.post("/api/webhooks/twilio/incoming")
def twilio_incoming():
    if not valid_twilio_signature():
        return "Invalid signature", 403
    parts = request.form.get("Body", "").strip().split()
    action = {"1": "acknowledged", "2": "in_progress", "3": "resolved"}.get(parts[0] if parts else "")
    if not action or len(parts) < 2 or not parts[1].isdigit():
        reply = "Formato inválido. Responda 1 ID para ciência, 2 ID para atendimento ou 3 ID para resolver."
    else:
        anomaly_id = int(parts[1])
        sender = request.form.get("From", "Responsável via Twilio")
        found = runtime().database.update_anomaly_status(anomaly_id, action, "Atualização recebida pelo WhatsApp/SMS.", sender)
        reply = f"BoxTwin #{anomaly_id} atualizado para {action}." if found else "Anomalia não encontrada."
    escaped = reply.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped}</Message></Response>', 200, {"Content-Type": "application/xml"}


@bp.get("/manifest.webmanifest")
def manifest():
    return current_app.send_static_file("manifest.webmanifest")


@bp.get("/service-worker.js")
def service_worker():
    return current_app.send_static_file("service-worker.js")


@bp.post("/api/demo/level/<float:level>")
def demo_level(level):
    sensor = runtime().sensor
    if not hasattr(sensor, "set_level"):
        return jsonify({"error": "Disponível somente no modo mock."}), 400
    sensor.set_level(level)
    return jsonify({"level_percent": sensor.level_percent})


@bp.get("/api/demo/scenarios")
def demo_scenarios():
    sensor = runtime().sensor
    if not hasattr(sensor, "list_scenarios"):
        return jsonify({"error": "Disponível somente no modo simulado."}), 400
    return jsonify({"scenarios": sensor.list_scenarios(), "active": sensor.scenario})


@bp.post("/api/demo/scenario/<scenario>")
def demo_scenario(scenario):
    sensor = runtime().sensor
    if not hasattr(sensor, "set_scenario"):
        return jsonify({"error": "Disponível somente no modo simulado."}), 400
    try:
        sensor.set_scenario(scenario)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    if scenario == "empty":
        runtime().calibrate()
    result = runtime().capture()
    return jsonify(result), 201


@bp.post("/api/demo/setup")
def demo_setup():
    sensor = runtime().sensor
    if not hasattr(sensor, "set_scenario"):
        return jsonify({"error": "Disponível somente no modo simulado."}), 400
    sensor.set_scenario("empty")
    calibration = runtime().calibrate()
    sensor.set_scenario("pile")
    reading = runtime().capture()
    return jsonify({"calibration": calibration, "reading": reading}), 201

```

### 📄 `boxtwin\runtime.py`

```python
import threading
import time

from .sensors import build_sensor
from pathlib import Path

from .services import AlertService, CalibrationService, GrokService, NotificationService, RagService, VolumeService


class BoxTwinRuntime:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.sensor = build_sensor(config["SENSOR_MODE"], config["BOX_HEIGHT_M"])
        self.calibration = CalibrationService(config["CALIBRATION_PATH"])
        self.volume = VolumeService(config["BOX_LENGTH_M"], config["BOX_WIDTH_M"], config["BOX_HEIGHT_M"])
        self.alerts = AlertService(config["CAPACITY_ALERT_PERCENT"], config["MIN_CONFIDENCE_PERCENT"])
        self.notifications = NotificationService(config, database)
        self.rag = RagService(Path(__file__).parent / "knowledge" / "procedures.json")
        self.assistant = GrokService(config, self.rag)
        self._stop = threading.Event()
        self._thread = None

    def calibrate(self):
        grid = self.sensor.read_distance_grid_mm()
        self.calibration.save(grid)
        return {"calibrated": True, "zones": 64, "message": "Linha de base do box vazio salva."}

    def capture(self):
        empty = self.calibration.load()
        if empty is None:
            return {"status": "not_calibrated", "message": "Calibre o box vazio antes de medir."}
        current = self.sensor.read_distance_grid_mm()
        metrics = self.volume.calculate(empty, current)
        reference_percent = getattr(self.sensor, "reference_percent", None)
        reference_error = (
            round(abs(metrics["capacity_percent"] - reference_percent), 2)
            if reference_percent is not None else None
        )
        alerts = self.alerts.evaluate(metrics)
        reading = {
            **metrics,
            "node_id": self.config["BOX_NODE_ID"],
            "sensor_mode": self.config["SENSOR_MODE"],
            "scenario": getattr(self.sensor, "scenario", "physical"),
            "reference_percent": reference_percent,
            "reference_error_points": reference_error,
            "distance_grid_mm": current,
            "status": "alert" if alerts else "normal",
            "alerts": alerts,
        }
        reading_id, created_at = self.database.save_reading(reading)
        anomaly_records = self.database.save_anomalies(reading_id, alerts)
        self.notifications.dispatch(anomaly_records)
        return {**reading, "id": reading_id, "created_at": created_at, "anomaly_ids": [a["id"] for a in anomaly_records]}

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, name="boxtwin-capture", daemon=True)
        self._thread.start()

    def _loop(self):
        while not self._stop.is_set():
            try:
                if self.calibration.load() is not None:
                    self.capture()
            except Exception as exc:
                print(f"[BoxTwin] Falha de leitura: {exc}")
            try:
                self.notifications.dispatch_escalations()
            except Exception as exc:
                print(f"[BoxTwin] Falha no escalonamento: {exc}")
            self._stop.wait(self.config["SAMPLE_INTERVAL_SECONDS"])

```

### 📄 `boxtwin\services.py`

```python
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

```

### 📄 `boxtwin\__init__.py`

```python
from pathlib import Path

from flask import Flask

from .config import load_config
from .database import Database
from .routes import bp
from .runtime import BoxTwinRuntime


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.update(load_config())
    if test_config:
        app.config.update(test_config)
    app.secret_key = app.config["SECRET_KEY"]

    Path(app.config["DATABASE_PATH"]).parent.mkdir(parents=True, exist_ok=True)
    Path(app.config["CALIBRATION_PATH"]).parent.mkdir(parents=True, exist_ok=True)

    database = Database(app.config["DATABASE_PATH"])
    database.initialize()
    runtime = BoxTwinRuntime(app.config, database)
    app.extensions["boxtwin_runtime"] = runtime
    app.register_blueprint(bp)

    if not app.config.get("TESTING"):
        runtime.start()

    return app

```

### 📄 `boxtwin\knowledge\procedures.json`

```json
[
  {"id":"PROC-001","title":"Capacidade próxima do limite","tags":["capacity","capacidade","volume","cheio"],"content":"Confirme a leitura em duas capturas consecutivas, suspenda nova alimentação do box, sinalize a operação e programe retirada ou redistribuição do material."},
  {"id":"PROC-002","title":"Baixa confiança de leitura","tags":["confidence","confiança","sensor","leitura"],"content":"Inspecione fixação e alinhamento do sensor, limpe cuidadosamente a janela óptica, confirme iluminação e vibração e execute nova calibração somente com o box vazio."},
  {"id":"PROC-003","title":"Possível obstrução","tags":["obstruction","obstrução","zonas","poeira"],"content":"Interrompa a medição automática, verifique poeira ou objeto diante do sensor, faça limpeza segura, capture novamente e encaminhe para manutenção se menos de 48 zonas permanecerem válidas."},
  {"id":"PROC-004","title":"Divergência volumétrica","tags":["erro","volume","calibração","divergência"],"content":"Compare as dimensões cadastradas com as dimensões internas reais, valide a linha de base vazia, repita três leituras e registre a diferença contra um volume conhecido."}
]

```

### 📄 `boxtwin\sensors\base.py`

```python
from abc import ABC, abstractmethod


class DepthSensor(ABC):
    @abstractmethod
    def read_distance_grid_mm(self):
        """Retorna uma lista 8×8 de distâncias em milímetros; use None para zona inválida."""


```

### 📄 `boxtwin\sensors\mock.py`

```python
import math
import random

from .base import DepthSensor


class MockSensor(DepthSensor):
    """Sensor virtual 8x8 para demonstrar o MVP sem hardware físico."""

    SCENARIOS = {
        "empty": {"label": "Box vazio", "description": "Linha de base para calibração."},
        "flat_25": {"label": "Carga uniforme 25%", "description": "Superfície plana em baixa ocupação."},
        "flat_50": {"label": "Carga uniforme 50%", "description": "Meia capacidade com superfície plana."},
        "flat_75": {"label": "Carga uniforme 75%", "description": "Carga elevada e distribuída."},
        "full": {"label": "Box quase cheio", "description": "Ocupação próxima do limite configurado."},
        "pile": {"label": "Pilha central", "description": "Monte de fertilizante com pico no centro."},
        "slope": {"label": "Superfície inclinada", "description": "Carga acumulada em uma das laterais."},
        "irregular": {"label": "Carga irregular", "description": "Ondulações e distribuição não uniforme."},
        "obstruction": {"label": "Sensor parcialmente obstruído", "description": "Simula zonas inválidas e baixa confiança."},
    }

    def __init__(self, box_height_m):
        self.empty_distance_mm = box_height_m * 1000
        self.box_height_m = box_height_m
        self.level_percent = 0.0
        self.scenario = "empty"
        self._capture_count = 0

    def set_level(self, level_percent):
        self.level_percent = max(0.0, min(float(level_percent), 100.0))
        self.scenario = "custom"

    def set_scenario(self, scenario):
        if scenario not in self.SCENARIOS:
            raise ValueError(f"Cenário desconhecido: {scenario}")
        self.scenario = scenario
        presets = {"empty": 0, "flat_25": 25, "flat_50": 50, "flat_75": 75, "full": 92}
        self.level_percent = presets.get(scenario, 0)

    def list_scenarios(self):
        return [{"id": key, **value} for key, value in self.SCENARIOS.items()]

    def _height_ratio(self, row, col):
        if self.scenario in {"empty", "flat_25", "flat_50", "flat_75", "full", "custom"}:
            return self.level_percent / 100

        x = (col - 3.5) / 3.5
        y = (row - 3.5) / 3.5
        radius = math.sqrt(x * x + y * y)
        if self.scenario in {"pile", "obstruction"}:
            return max(0.08, 0.86 * (1 - radius / 1.42))
        if self.scenario == "slope":
            return 0.18 + 0.62 * ((col + row) / 14)
        if self.scenario == "irregular":
            wave = 0.48 + 0.16 * math.sin(col * 1.35) + 0.12 * math.cos(row * 1.7)
            bump = 0.20 * math.exp(-((x + 0.35) ** 2 + (y - 0.2) ** 2) / 0.22)
            return max(0.08, min(wave + bump, 0.88))
        return 0.0

    @property
    def reference_percent(self):
        ratios = [self._height_ratio(row, col) for row in range(8) for col in range(8)]
        return round(sum(ratios) / 64 * 100, 1)

    def read_distance_grid_mm(self):
        self._capture_count += 1
        rng = random.Random(f"{self.scenario}-{self._capture_count}")
        grid = []
        for row in range(8):
            line = []
            for col in range(8):
                if self.scenario == "obstruction" and (
                    (row < 4 and col >= 4) or (row in {4, 5} and col >= 6)
                ):
                    line.append(None)
                    continue
                height_mm = self.empty_distance_mm * self._height_ratio(row, col)
                noise = 0 if self.scenario == "empty" else rng.uniform(-1.8, 1.8)
                line.append(round(max(0, self.empty_distance_mm - height_mm + noise), 2))
            grid.append(line)
        return grid

```

### 📄 `boxtwin\sensors\vl53l5cx.py`

```python
from .base import DepthSensor


class VL53L5CXSensor(DepthSensor):
    """Ponto de integração com o driver físico da placa breakout adquirida."""

    def __init__(self):
        raise RuntimeError(
            "Driver físico ainda não configurado. Use SENSOR_MODE=mock até instalar "
            "o pacote indicado pelo fabricante da placa VL53L5CX."
        )

    def read_distance_grid_mm(self):
        raise NotImplementedError


```

### 📄 `boxtwin\sensors\vl53l8cx.py`

```python
from .base import DepthSensor


class VL53L8CXSensor(DepthSensor):
    """Adaptador reservado para a placa VL53L8CX física.

    O painel e o cálculo já esperam uma matriz 8x8 em milímetros. Quando a
    placa for adquirida, somente este adaptador precisará receber o driver
    indicado pelo fabricante da breakout.
    """

    def __init__(self):
        raise RuntimeError(
            "Driver do VL53L8CX ainda não configurado. Use SENSOR_MODE=mock "
            "para o Hackathon sem o hardware físico."
        )

    def read_distance_grid_mm(self):
        raise NotImplementedError

```

### 📄 `boxtwin\sensors\__init__.py`

```python
from .mock import MockSensor
from .vl53l5cx import VL53L5CXSensor
from .vl53l8cx import VL53L8CXSensor


def build_sensor(mode, box_height_m):
    if mode == "mock":
        return MockSensor(box_height_m)
    if mode == "vl53l5cx":
        return VL53L5CXSensor()
    if mode == "vl53l8cx":
        return VL53L8CXSensor()
    raise ValueError(f"SENSOR_MODE desconhecido: {mode}")

```

### 📄 `boxtwin\static\admin.js`

```javascript
const $ = id => document.getElementById(id);
const escapeHtml = text => String(text ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
async function api(url, options={}) { const response=await fetch(url,options); const data=await response.json(); if(response.status===401){location.href='/login';throw new Error('Sessão expirada.');} if(!response.ok)throw new Error(data.error||'Falha.'); return data; }
async function loadAdmin(){
  const [anomalies, notifications, recipients, rules]=await Promise.all([api('/api/admin/anomalies?limit=50'),api('/api/admin/notifications?limit=30'),api('/api/admin/recipients'),api('/api/admin/rules')]);
  $('anomalyList').innerHTML=anomalies.length?anomalies.map(a=>`<article class="incident ${a.severity}"><div><a href="/admin/anomalies/${a.id}"><b>#${a.id} · ${escapeHtml(a.message)}</b></a><small>${new Date(a.created_at).toLocaleString('pt-BR')} · ${escapeHtml(a.anomaly_type)}</small></div><span class="badge">${escapeHtml(a.status)}</span>${a.status==='open'?`<button onclick="ack(${a.id})" class="secondary compact">Registrar ciência</button>`:''}<button onclick="ask('${escapeHtml(a.anomaly_type)} ${escapeHtml(a.message)}')" class="secondary compact">Sugerir tratativa</button></article>`).join(''):'<p class="muted">Nenhuma anomalia registrada.</p>';
  $('notificationList').innerHTML=notifications.length?notifications.map(n=>`<div class="notification-row"><b>${escapeHtml(n.channel)}</b><span>${escapeHtml(n.status)}</span><small>${new Date(n.created_at).toLocaleString('pt-BR')}</small></div>`).join(''):'<p class="muted">E-mail e Twilio estão prontos, mas desativados até a configuração das credenciais.</p>';
  $('recipientList').innerHTML=recipients.map(r=>`<div class="list-row"><b>${escapeHtml(r.name)}</b><span>${escapeHtml(r.team_name||r.recipient_type)}</span><small>${escapeHtml(r.email||r.phone)}</small></div>`).join('')||'<p class="muted">Cadastre o primeiro responsável.</p>';
  $('ruleRecipient').innerHTML=recipients.filter(r=>r.active).map(r=>`<option value="${r.id}">${escapeHtml(r.name)}</option>`).join('');
  $('ruleList').innerHTML=rules.map(r=>`<div class="list-row"><b>${escapeHtml(r.anomaly_type)} → ${escapeHtml(r.recipient_name)}</b><span>${escapeHtml(r.channel)}</span><small>${r.escalation_minutes?`Após ${r.escalation_minutes} min`:'Imediata'}</small></div>`).join('')||'<p class="muted">Nenhuma regra cadastrada.</p>';
}
async function ack(id){await api(`/api/admin/anomalies/${id}/acknowledge`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({note:'Ciência registrada no painel.'})});await loadAdmin();}
async function ask(text){$('assistantQuestion').value=text;await queryAssistant(text);}
async function queryAssistant(question){$('assistantAnswer').textContent='Consultando base de procedimentos…';try{const r=await api('/api/admin/assistant',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question})});$('assistantAnswer').innerHTML=`<p>${escapeHtml(r.answer)}</p><small>Fontes: ${r.sources.map(s=>escapeHtml(s.id+' — '+s.title)).join('; ')||'nenhuma'}</small>`;}catch(e){$('assistantAnswer').textContent=e.message;}}
$('assistantForm').onsubmit=e=>{e.preventDefault();queryAssistant($('assistantQuestion').value)};$('refreshAdmin').onclick=loadAdmin;
$('recipientForm').onsubmit=async e=>{e.preventDefault();await api('/api/admin/recipients',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:$('recipientName').value,recipient_type:$('recipientType').value,team_name:$('recipientTeam').value,email:$('recipientEmail').value,phone:$('recipientPhone').value})});e.target.reset();await loadAdmin();};
$('ruleForm').onsubmit=async e=>{e.preventDefault();await api('/api/admin/rules',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({anomaly_type:$('ruleType').value,severity:$('ruleSeverity').value,recipient_id:$('ruleRecipient').value,channel:$('ruleChannel').value,escalation_minutes:$('ruleDelay').value})});await loadAdmin();};
const stream=new EventSource('/api/stream');stream.addEventListener('reading',()=>{ $('adminConnection').textContent='Online';loadAdmin();});stream.onerror=()=>{$('adminConnection').textContent='Reconectando…';};
loadAdmin();

```

### 📄 `boxtwin\static\anomaly.js`

```javascript
const $=id=>document.getElementById(id);let detail;
const safe=v=>String(v??'—').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
async function api(url,options={}){const r=await fetch(url,options);const d=await r.json();if(r.status===401){location.href='/login';throw new Error('Sessão expirada');}if(!r.ok)throw new Error(d.error||'Falha');return d;}
function renderGrid(reading){const box=$('incidentGrid');box.innerHTML='';(reading?.height_grid_m||[]).flat().forEach(v=>{const c=document.createElement('div');c.className='cell';c.textContent=(v*100).toFixed(1);c.style.opacity=.45+Math.min(1,v/(reading.maximum_height_m||1))*.55;box.appendChild(c);});}
async function load(){detail=await api(`/api/admin/anomalies/${window.ANOMALY_ID}`);const a=detail.anomaly,r=detail.reading;$('incidentSummary').innerHTML=`<div><span class="eyebrow">${safe(a.severity)} · ${safe(a.status)}</span><h2>${safe(a.message)}</h2><p>${new Date(a.created_at).toLocaleString('pt-BR')} · ${safe(r?.node_id)}</p></div>`;$('readingDetail').innerHTML=`<div><small>Ocupação</small><b>${r?.capacity_percent??'—'}%</b></div><div><small>Volume</small><b>${r?.volume_m3??'—'} m³</b></div><div><small>Confiança</small><b>${r?.confidence_percent??'—'}%</b></div><div><small>Zonas válidas</small><b>${r?.valid_zones??'—'}/64</b></div>`;renderGrid(r);$('timeline').innerHTML=[{created_at:a.created_at,actor:'BoxTwin',event_type:'detected',note:a.message},...detail.events].map(e=>`<div class="timeline-event"><b>${safe(e.event_type)}</b><span>${safe(e.actor)}</span><small>${new Date(e.created_at).toLocaleString('pt-BR')}</small><p>${safe(e.note)}</p></div>`).join('');}
$('statusForm').onsubmit=async e=>{e.preventDefault();await api(`/api/admin/anomalies/${window.ANOMALY_ID}/status`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:$('incidentStatus').value,note:$('incidentNote').value})});await load();};
$('suggestTreatment').onclick=async()=>{const a=detail.anomaly,r=detail.reading;$('treatment').textContent='Analisando…';const result=await api('/api/admin/assistant',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:`Como tratar ${a.anomaly_type}: ${a.message}?`,context:r})});$('treatment').innerHTML=`<p>${safe(result.answer)}</p><small>Modo: ${safe(result.mode)} · Fontes: ${result.sources.map(s=>safe(s.id)).join(', ')}</small>`;};load();

```

### 📄 `boxtwin\static\app.js`

```javascript
const $ = id => document.getElementById(id);
const state = { latest: null, health: null, activeScenario: null };

function fmt(value, digits = 1) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(digits) : '—';
}

function colorFor(value, max) {
  const ratio = Math.max(0, Math.min(1, value / Math.max(max, .001)));
  const stops = [[18,58,112],[20,151,218],[24,213,255],[255,181,71]];
  const scaled = ratio * (stops.length - 1);
  const index = Math.min(stops.length - 2, Math.floor(scaled));
  const part = scaled - index;
  const rgb = stops[index].map((v, i) => Math.round(v + (stops[index + 1][i] - v) * part));
  return `rgb(${rgb.join(',')})`;
}

function renderGrid(data) {
  const grid = $('grid');
  grid.innerHTML = '';
  const values = data.height_grid_m.flat();
  const max = Math.max(...values, .001);
  values.forEach(value => {
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.style.background = colorFor(value, max);
    cell.textContent = (value * 100).toFixed(1);
    cell.title = `Altura: ${(value * 100).toFixed(2)} cm`;
    grid.appendChild(cell);
  });
}

function sizeCanvas(canvas) {
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(1, Math.round(rect.width * ratio));
  canvas.height = Math.max(1, Math.round(rect.height * ratio));
  const context = canvas.getContext('2d');
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  return { context, width: rect.width, height: rect.height };
}

function drawTwin(grid) {
  const canvas = $('twinCanvas');
  const { context: ctx, width, height } = sizeCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  const maxValue = Math.max(...grid.flat(), .001);
  const centerX = width * .50, originY = height * .76;
  const scaleX = Math.min(width / 19, 31), scaleY = scaleX * .48, scaleZ = height * 1.22;
  const project = (row, col, z = 0) => ({
    x: centerX + (col - row) * scaleX,
    y: originY + (col + row - 7) * scaleY - z * scaleZ
  });

  ctx.strokeStyle = '#78b8df55'; ctx.lineWidth = 1;
  const base = [project(0,0), project(0,7), project(7,7), project(7,0)];
  ctx.beginPath(); base.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y)); ctx.closePath();
  ctx.fillStyle = '#0a2238'; ctx.fill(); ctx.stroke();

  for (let sum = 0; sum <= 12; sum++) {
    for (let row = 0; row < 7; row++) {
      const col = sum - row;
      if (col < 0 || col >= 7) continue;
      const corners = [
        [row,col,grid[row][col]], [row,col+1,grid[row][col+1]],
        [row+1,col+1,grid[row+1][col+1]], [row+1,col,grid[row+1][col]]
      ].map(([r,c,z]) => project(r,c,z));
      const avg = (grid[row][col] + grid[row][col+1] + grid[row+1][col+1] + grid[row+1][col]) / 4;
      ctx.beginPath(); corners.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y)); ctx.closePath();
      ctx.fillStyle = colorFor(avg, maxValue); ctx.globalAlpha = .88; ctx.fill();
      ctx.globalAlpha = 1; ctx.strokeStyle = '#d8f5ff55'; ctx.stroke();
    }
  }

  ctx.strokeStyle = '#9bdcffaa'; ctx.lineWidth = 1.2;
  [[0,0],[0,7],[7,7],[7,0]].forEach(([r,c]) => {
    const bottom = project(r,c,0), top = project(r,c,state.health?.dimensions_m?.height || .5);
    ctx.beginPath(); ctx.moveTo(bottom.x,bottom.y); ctx.lineTo(top.x,top.y); ctx.stroke();
  });
  ctx.fillStyle = '#b8d4e8'; ctx.font = '11px Segoe UI';
  ctx.fillText('Superfície estimada da carga', 15, 22);
}

function drawHistory(items) {
  const canvas = $('historyCanvas');
  const { context: ctx, width, height } = sizeCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  const pad = { left: 38, right: 14, top: 15, bottom: 24 };
  const w = width - pad.left - pad.right, h = height - pad.top - pad.bottom;
  ctx.font = '10px Segoe UI'; ctx.fillStyle = '#708196'; ctx.strokeStyle = '#dce5ef'; ctx.lineWidth = 1;
  [0,25,50,75,100].forEach(value => {
    const y = pad.top + h * (1 - value / 100);
    ctx.beginPath(); ctx.moveTo(pad.left,y); ctx.lineTo(width-pad.right,y); ctx.stroke();
    ctx.fillText(`${value}%`, 5, y + 3);
  });
  if (!items.length) return;
  const points = items.map((item,index) => ({
    x: pad.left + (items.length === 1 ? w / 2 : index * w / (items.length - 1)),
    y: pad.top + h * (1 - Math.min(100,item.capacity_percent) / 100)
  }));
  const gradient = ctx.createLinearGradient(0,pad.top,0,pad.top+h);
  gradient.addColorStop(0,'rgba(23,105,255,.30)'); gradient.addColorStop(1,'rgba(23,105,255,0)');
  ctx.beginPath(); points.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y));
  ctx.lineTo(points.at(-1).x,pad.top+h); ctx.lineTo(points[0].x,pad.top+h); ctx.closePath(); ctx.fillStyle=gradient; ctx.fill();
  ctx.beginPath(); points.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y));
  ctx.strokeStyle='#1769ff'; ctx.lineWidth=2.5; ctx.stroke();
  points.forEach(p => {ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fillStyle='#fff';ctx.fill();ctx.strokeStyle='#1769ff';ctx.stroke();});
}

function setActiveScenario(id) {
  state.activeScenario = id;
  document.querySelectorAll('.scenario').forEach(button => button.classList.toggle('active', button.dataset.id === id));
}

function render(data) {
  if (!data || !data.id) return;
  state.latest = data;
  $('volume').textContent = fmt(data.volume_m3, 4);
  $('capacity').textContent = fmt(data.capacity_percent, 1);
  $('capacityBar').style.width = `${Math.min(100, data.capacity_percent)}%`;
  $('avgHeight').textContent = fmt((data.average_height_m || 0) * 100, 1);
  $('maxHeight').textContent = `Pico: ${fmt((data.maximum_height_m || 0) * 100, 1)} cm`;
  $('confidence').textContent = fmt(data.confidence_percent, 1);
  $('zones').textContent = data.valid_zones;
  $('referenceError').textContent = fmt(data.reference_error_points, 2);
  $('referenceValue').textContent = data.reference_percent == null ? 'Referência indisponível no sensor real' : `Referência: ${fmt(data.reference_percent,1)}%`;
  $('updated').textContent = `Atualizado ${new Date(data.created_at).toLocaleString('pt-BR')}`;
  setActiveScenario(data.scenario);
  renderGrid(data); drawTwin(data.height_grid_m);
  $('alerts').innerHTML = data.alerts.length
    ? data.alerts.map(alert => `<div class="alert ${alert.level}">${alert.message}</div>`).join('')
    : '<div class="alert ok">Operação normal. Nenhum alerta ativo.</div>';
}

async function request(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || data.message || 'Falha na operação.');
  return data;
}

async function loadHistory() {
  const items = await request('/api/readings/history?limit=20');
  drawHistory(items);
}

async function chooseScenario(id, button) {
  const buttons = document.querySelectorAll('.scenario'); buttons.forEach(item => item.disabled = true);
  try { render(await request(`/api/demo/scenario/${id}`, {method:'POST'})); await loadHistory(); }
  catch (error) { alert(error.message); }
  finally { buttons.forEach(item => item.disabled = false); }
}

async function loadScenarios() {
  if (!state.health.demo_enabled) { $('demoPanel').hidden = true; return; }
  const data = await request('/api/demo/scenarios');
  $('scenarios').innerHTML = '';
  data.scenarios.forEach(item => {
    const button = document.createElement('button'); button.className='scenario'; button.dataset.id=item.id;
    button.textContent=item.label; button.title=item.description; button.onclick=()=>chooseScenario(item.id,button);
    $('scenarios').appendChild(button);
  });
  setActiveScenario(data.active);
}

async function initialize() {
  try {
    state.health = await request('/api/health');
    $('connection').textContent='● BoxNode online'; $('connection').classList.add('online');
    const d=state.health.dimensions_m;
    $('boxCapacity').textContent=`${fmt(state.health.capacity_m3,3)} m³`;
    $('boxDimensions').textContent=`${d.length} m × ${d.width} m × ${d.height} m`;
    if (!state.health.demo_enabled) { $('modeBadge').textContent='SENSOR FÍSICO'; $('modeBadge').classList.remove('demo'); }
    await loadScenarios();
    const latest = await request('/api/readings/latest');
    if (latest.status === 'no_data' && state.health.demo_enabled) {
      const setup = await request('/api/demo/setup',{method:'POST'}); render(setup.reading);
    } else render(latest);
    await loadHistory();
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/service-worker.js').catch(()=>{});
    const stream = new EventSource('/api/stream');
    stream.addEventListener('reading', event => { const reading=JSON.parse(event.data); if(reading.id!==state.latest?.id){render(reading);loadHistory().catch(()=>{});} });
    stream.onerror=()=>{$('connection').textContent='● Reconectando…';};
    stream.onopen=()=>{$('connection').textContent='● BoxNode online';};
  } catch (error) {
    $('connection').textContent='● Sem conexão'; $('connection').classList.remove('online');
    $('alerts').innerHTML=`<div class="alert danger">${error.message}</div>`;
  }
}

$('setup').onclick = async () => { const data=await request('/api/demo/setup',{method:'POST'});render(data.reading);await loadHistory(); };
$('capture').onclick = async () => { try{render(await request('/api/readings',{method:'POST'}));await loadHistory();}catch(error){alert(error.message);} };
$('calibrate').onclick = async () => {
  if (!confirm('A calibração definirá o box como vazio. Deseja continuar?')) return;
  try {
    if (state.health.demo_enabled) render(await request('/api/demo/scenario/empty',{method:'POST'}));
    else { await request('/api/calibration',{method:'POST'}); alert('Calibração salva.'); }
    await loadHistory();
  } catch(error){alert(error.message);}
};
window.addEventListener('resize',()=>{if(state.latest)drawTwin(state.latest.height_grid_m);loadHistory().catch(()=>{});});
initialize();

```

### 📄 `boxtwin\static\service-worker.js`

```javascript
const CACHE='boxtwin-v3';const ASSETS=['/','/static/style.css','/static/app.js','/manifest.webmanifest'];self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));self.addEventListener('fetch',e=>{if(e.request.method==='GET'&&!e.request.url.includes('/api/'))e.respondWith(fetch(e.request).then(r=>{const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));return r;}).catch(()=>caches.match(e.request)));});

```

### 📄 `boxtwin\static\style.css`

```css
:root{--navy:#061426;--navy2:#0b2542;--blue:#1769ff;--cyan:#18d4ff;--green:#1fd19b;--amber:#ffb547;--red:#ef5b67;--paper:#eef3f8;--ink:#142238;--muted:#6f8095;--line:#dce5ef;--card:#fff}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,"Segoe UI",Arial,sans-serif}.topbar{display:flex;justify-content:space-between;align-items:center;padding:23px max(4vw,24px);color:white;background:radial-gradient(circle at 80% 0,#194c7b 0,transparent 32%),linear-gradient(125deg,var(--navy),#0a2038);border-bottom:1px solid #ffffff17}.brand,.status-group{display:flex;align-items:center;gap:13px}.brand-mark{display:grid;place-items:center;width:46px;height:46px;border:1px solid #36c8ff80;border-radius:14px;background:#0a3153;color:var(--cyan);font-size:25px;font-weight:900}.brand span,.eyebrow{font-size:10px;letter-spacing:.17em;font-weight:900;color:#1285ce}.brand span{color:var(--cyan)}h1{margin:3px 0 1px;font-size:23px}.brand p{margin:0;color:#aebfd1;font-size:12px}.badge{padding:8px 11px;border:1px solid #ffffff1f;border-radius:99px;background:#21374e;font-size:10px;letter-spacing:.05em}.badge.demo{color:#8de9ff;background:#0a405a}.badge.online{color:#65e4b9;background:#123f3c}main{width:min(1320px,94vw);margin:24px auto}.hero{display:grid;grid-template-columns:1fr auto;align-items:center;gap:30px;margin-bottom:18px;padding:24px 27px;border-radius:19px;color:white;background:linear-gradient(120deg,#0a2542,#103b61);box-shadow:0 16px 38px #09243d1c}.hero h2{margin:5px 0 7px;font-size:clamp(25px,3vw,38px)}.hero p{max-width:760px;margin:0;color:#b9c9d8;line-height:1.55}.box-spec{min-width:220px;padding:18px;border-left:1px solid #ffffff20}.box-spec span,.box-spec small{display:block;color:#adbed0}.box-spec strong{display:block;margin:5px 0;font-size:30px}.metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:13px}.metrics article,.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:0 10px 30px #1029440a}.metrics article{padding:18px}.metrics small{display:block;color:var(--muted);font-weight:650}.metrics strong{font-size:31px;margin-right:4px}.metrics span,.metrics em{color:var(--muted)}.metrics em{display:block;margin-top:5px;font-size:11px;font-style:normal}.meter{height:5px;margin-top:9px;overflow:hidden;border-radius:10px;background:#e7eef6}.meter i{display:block;width:0;height:100%;border-radius:10px;background:linear-gradient(90deg,var(--green),var(--amber),var(--red));transition:width .4s}.panel{padding:20px}.demo-panel{margin-top:15px;border-color:#bdeafa;background:linear-gradient(115deg,#f9fdff,#effaff)}.demo-panel>p{margin:5px 0 13px;color:var(--muted)}.panel-heading{display:flex;justify-content:space-between;align-items:center;gap:12px}.panel h3{margin:3px 0 12px;font-size:17px}.scenario-list{display:flex;flex-wrap:wrap;gap:8px}.scenario{width:auto;margin:0;padding:9px 12px;border:1px solid #c9d9e9;background:white;color:#31506d}.scenario:hover,.scenario.active{border-color:var(--blue);background:#e9f1ff;color:#0755cd}.workspace{display:grid;grid-template-columns:1.45fr 1fr .72fr;gap:15px;margin-top:15px}.twin-panel canvas{display:block;width:100%;height:330px;border-radius:12px;background:linear-gradient(#071a2e,#0b2d4a)}.map-panel{min-width:0}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:5px;aspect-ratio:1}.cell{display:grid;place-items:center;min-width:0;border-radius:6px;color:#fff;font-size:9px;font-weight:800;background:#cbd8e7;transition:transform .2s}.cell:hover{transform:scale(1.06)}.unit,.muted{font-size:11px;color:var(--muted)}.legend{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:10px;color:var(--muted);font-size:10px}.legend i{width:150px;height:7px;border-radius:8px;background:linear-gradient(90deg,#123a70,#16d5ff,#ffb547)}.alerts{min-height:180px}.alerts p{color:var(--muted);line-height:1.5}.alert{padding:10px;margin:8px 0;border-radius:9px;background:#fff3d9;border-left:4px solid var(--amber);font-size:12px}.alert.danger{background:#ffe7ea;border-color:var(--red)}.alert.ok{background:#e4faf3;border-color:var(--green)}button{width:100%;padding:12px;margin-top:9px;border:0;border-radius:9px;font-weight:800;cursor:pointer;transition:filter .2s,transform .2s}button:hover{filter:brightness(.97);transform:translateY(-1px)}button:disabled{opacity:.55;cursor:wait}.primary{background:var(--blue);color:white}.secondary{background:#e7eef8;color:#174775}.compact{width:auto;margin:0;padding:10px 14px}.history-panel{margin-top:15px}.history-panel canvas{display:block;width:100%;height:170px}footer{display:flex;justify-content:space-between;align-items:center;padding:25px 4px;color:var(--muted);font-size:12px}footer span{font-weight:900;color:#31506d}@media(max-width:1100px){.metrics{grid-template-columns:repeat(3,1fr)}.workspace{grid-template-columns:1fr 1fr}.control-panel{grid-column:1/-1}.alerts{min-height:0}}@media(max-width:720px){.topbar,.hero,footer{align-items:flex-start;flex-direction:column}.status-group{flex-wrap:wrap}.hero{grid-template-columns:1fr}.box-spec{padding:12px 0 0;border-left:0;border-top:1px solid #ffffff20}.metrics{grid-template-columns:repeat(2,1fr)}.workspace{grid-template-columns:1fr}.control-panel{grid-column:auto}.panel-heading{align-items:flex-start}.demo-panel .panel-heading{flex-direction:column}.compact{width:100%}.twin-panel canvas{height:275px}.metrics strong{font-size:27px}}
/* Administração, autenticação e experiência móvel */
.topbar a{color:inherit;text-decoration:none}.topbar form{margin:0}.topbar button.badge{font:inherit;cursor:pointer}
.auth-page{min-height:100vh;display:grid;place-items:center;background:radial-gradient(circle at top,#12395b,#06111f 55%);padding:20px}
.auth-card{width:min(420px,100%);background:#fff;color:#122234;padding:32px;border-radius:22px;box-shadow:0 25px 70px #0008}.auth-card form{display:grid;gap:16px;margin:24px 0}.auth-card label{display:grid;gap:7px;font-weight:700}.auth-card input,.assistant-panel textarea{width:100%;box-sizing:border-box;border:1px solid #cad7e5;border-radius:10px;padding:12px;font:inherit}.auth-card .brand span,.auth-card .brand h1{color:#102c46}.auth-card a{color:#1769ff}
.admin-grid{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(300px,.85fr);gap:18px;margin-bottom:18px}.incident-list{display:grid;gap:10px}.incident{display:grid;grid-template-columns:1fr auto auto auto;align-items:center;gap:10px;padding:14px;border:1px solid #dce6ef;border-left:4px solid #f0a928;border-radius:10px}.incident.danger{border-left-color:#dc3545}.incident small{display:block;color:#708196;margin-top:4px}.assistant-panel form{display:grid;gap:10px}.assistant-answer{min-height:100px;background:#eef6fc;border-radius:12px;padding:14px;margin:14px 0}.notification-list{display:grid;gap:8px}.notification-row{display:grid;grid-template-columns:1fr 1fr 2fr;gap:12px;padding:10px;border-bottom:1px solid #dce6ef}
@media(max-width:760px){.topbar{align-items:flex-start;gap:12px}.status-group{flex-wrap:wrap}.admin-grid{grid-template-columns:1fr}.incident{grid-template-columns:1fr 1fr}.incident>div{grid-column:1/-1}.notification-row{grid-template-columns:1fr 1fr}.notification-row small{grid-column:1/-1}.auth-card{padding:24px}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.workspace{display:block}.workspace>*{margin-bottom:16px}.hero{display:block}.box-spec{margin-top:16px}.scenario-list{display:grid;grid-template-columns:1fr 1fr}}
@media(max-width:430px){.metrics{grid-template-columns:1fr}.scenario-list{grid-template-columns:1fr}.topbar{padding:14px}.brand h1{font-size:1.15rem}main{padding:12px}.panel{padding:14px}.incident{grid-template-columns:1fr}.incident>*{grid-column:1/-1}}
.inline-form,.stack-form{display:grid;gap:10px;margin:14px 0}.inline-form{grid-template-columns:repeat(2,minmax(0,1fr))}.inline-form input,.inline-form select,.stack-form select,.stack-form textarea{border:1px solid #cad7e5;border-radius:9px;padding:10px;font:inherit;background:#fff}.inline-form button{grid-column:1/-1}.compact-list{display:grid;gap:7px}.list-row{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:10px;padding:10px;border-bottom:1px solid #dce6ef}.incident a{color:inherit;text-decoration:none}.incident a:hover{text-decoration:underline}.detail-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:15px 0}.detail-grid>div{background:#eef6fc;padding:12px;border-radius:10px}.detail-grid small,.detail-grid b{display:block}.timeline{border-left:2px solid #87b7d8;margin-left:8px;padding-left:20px}.timeline-event{position:relative;padding:0 0 20px}.timeline-event:before{content:'';position:absolute;width:10px;height:10px;border-radius:50%;background:#1769ff;left:-26px;top:4px}.timeline-event span,.timeline-event small{display:block;color:#708196}.timeline-event p{margin:.4rem 0}.management-grid{margin-top:18px}
@media(max-width:760px){.inline-form,.list-row,.detail-grid{grid-template-columns:1fr}.inline-form button{grid-column:auto}}

```

### 📄 `boxtwin\templates\admin.html`

```html
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#071526"><title>Admin | BoxTwin</title><link rel="manifest" href="/manifest.webmanifest"><link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header class="topbar"><div class="brand"><div class="brand-mark">H</div><div><span>HYDROGENI · ADMIN</span><h1>Central operacional</h1><p>{{ box_name }} · {{ node_id }}</p></div></div><div class="status-group"><a class="badge" href="/">Painel</a><form method="post" action="/logout"><button class="badge" type="submit">Sair</button></form></div></header><main>
<section class="hero"><div><span class="eyebrow">GESTÃO DE INCIDENTES</span><h2>Anomalias e tratativas assistidas</h2><p>Revise alertas, registre ciência e consulte procedimentos técnicos recuperados da base local.</p></div><div class="box-spec"><span>Estado do BoxNode</span><strong id="adminConnection">Conectando…</strong><small>Atualização por eventos em tempo real</small></div></section>
<section class="admin-grid"><article class="panel"><div class="panel-heading"><div><span class="eyebrow">FILA OPERACIONAL</span><h3>Anomalias</h3></div><button id="refreshAdmin" class="secondary compact">Atualizar</button></div><div id="anomalyList" class="incident-list"></div></article>
<aside class="panel assistant-panel"><span class="eyebrow">IA + RAG LOCAL</span><h3>Assistente de tratativas</h3><p>As sugestões citam os procedimentos internos usados como fonte.</p><div id="assistantAnswer" class="assistant-answer">Selecione uma anomalia ou descreva o problema.</div><form id="assistantForm"><textarea id="assistantQuestion" rows="4" placeholder="Ex.: Como tratar baixa confiança do sensor?" required></textarea><button class="primary" type="submit">Consultar procedimento</button></form></aside></section>
<section class="admin-grid management-grid"><article class="panel"><span class="eyebrow">RESPONSÁVEIS</span><h3>Destinatários e equipes</h3><form id="recipientForm" class="inline-form"><input id="recipientName" placeholder="Nome do responsável" required><select id="recipientType"><option value="administrator">Administrador</option><option value="team">Equipe</option></select><input id="recipientTeam" placeholder="Equipe/setor"><input id="recipientEmail" type="email" placeholder="E-mail"><input id="recipientPhone" placeholder="WhatsApp/SMS: +5598..."><button class="primary">Cadastrar</button></form><div id="recipientList" class="compact-list"></div></article><article class="panel"><span class="eyebrow">AUTOMAÇÃO</span><h3>Regras e escalonamento</h3><form id="ruleForm" class="inline-form"><select id="ruleType"><option value="*">Todas as anomalias</option><option value="capacity">Capacidade</option><option value="confidence">Baixa confiança</option><option value="obstruction">Obstrução</option></select><select id="ruleSeverity"><option value="*">Toda severidade</option><option value="warning">Atenção</option><option value="danger">Crítica</option></select><select id="ruleRecipient" required></select><select id="ruleChannel"><option value="email">E-mail</option><option value="twilio">Twilio</option></select><input id="ruleDelay" type="number" min="0" value="0" placeholder="Minutos"><button class="primary">Criar regra</button></form><div id="ruleList" class="compact-list"></div></article></section>
<section class="panel"><div class="panel-heading"><div><span class="eyebrow">CANAIS EXTERNOS</span><h3>Histórico de notificações</h3></div></div><div id="notificationList" class="notification-list"></div></section></main><script src="{{ url_for('static', filename='admin.js') }}"></script></body></html>

```

### 📄 `boxtwin\templates\anomaly.html`

```html
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#071526"><title>Incidente #{{ anomaly_id }} | BoxTwin</title><link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head><body>
<header class="topbar"><div class="brand"><div class="brand-mark">H</div><div><span>HYDROGENI · INCIDENTE</span><h1>Anomalia #{{ anomaly_id }}</h1></div></div><a class="badge" href="/admin">← Central operacional</a></header><main>
<section id="incidentSummary" class="hero"><div><span class="eyebrow">CARREGANDO</span><h2>Detalhes da ocorrência</h2></div></section>
<section class="admin-grid"><article class="panel"><span class="eyebrow">DADOS DA LEITURA</span><h3>Evidências</h3><div id="readingDetail" class="detail-grid"></div><div id="incidentGrid" class="grid"></div></article><aside class="panel"><span class="eyebrow">TRATATIVA</span><h3>Atualizar situação</h3><form id="statusForm" class="stack-form"><select id="incidentStatus"><option value="acknowledged">Ciente</option><option value="in_progress">Em atendimento</option><option value="resolved">Resolvida</option><option value="false_positive">Falso positivo</option></select><textarea id="incidentNote" rows="4" placeholder="Observação técnica"></textarea><button class="primary">Salvar atualização</button></form><button id="suggestTreatment" class="secondary">Sugerir tratativa com IA</button><div id="treatment" class="assistant-answer">Aguardando consulta.</div></aside></section>
<section class="panel"><span class="eyebrow">RASTREABILIDADE</span><h3>Linha do tempo</h3><div id="timeline" class="timeline"></div></section></main><script>window.ANOMALY_ID={{ anomaly_id }};</script><script src="{{ url_for('static', filename='anomaly.js') }}"></script></body></html>

```

### 📄 `boxtwin\templates\index.html`

```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#071526">
  <link rel="manifest" href="/manifest.webmanifest">
  <title>HydrogenI | BoxTwin 3D</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <div class="brand-mark">H</div>
      <div><span>HYDROGENI · BOXNODE</span><h1>BoxTwin 3D</h1><p>{{ box_name }} · {{ node_id }}</p></div>
    </div>
    <div class="status-group"><a href="/admin" class="badge">ÁREA ADMIN</a><b id="modeBadge" class="badge demo">MODO DEMONSTRAÇÃO</b><b id="connection" class="badge">Conectando…</b></div>
  </header>

  <main>
    <section class="hero">
      <div><span class="eyebrow">GÊMEO DIGITAL PARA GRANÉIS</span><h2>Volume do box em tempo real</h2><p>Protótipo demonstrável com matriz virtual 8×8. A mesma interface receberá as leituras do VL53L8CX quando o hardware estiver disponível.</p></div>
      <div class="box-spec"><span>Capacidade cadastrada</span><strong id="boxCapacity">—</strong><small id="boxDimensions">Carregando dimensões…</small></div>
    </section>

    <section class="metrics">
      <article><small>Volume estimado</small><div><strong id="volume">—</strong><span>m³</span></div><em>Integração das 64 zonas</em></article>
      <article><small>Ocupação</small><div><strong id="capacity">—</strong><span>%</span></div><div class="meter"><i id="capacityBar"></i></div></article>
      <article><small>Altura média</small><div><strong id="avgHeight">—</strong><span>cm</span></div><em id="maxHeight">Pico: —</em></article>
      <article><small>Confiança</small><div><strong id="confidence">—</strong><span>%</span></div><em><span id="zones">—</span> de 64 zonas válidas</em></article>
      <article><small>Erro da simulação</small><div><strong id="referenceError">—</strong><span>p.p.</span></div><em id="referenceValue">Referência: —</em></article>
    </section>

    <section id="demoPanel" class="demo-panel panel">
      <div class="panel-heading"><div><span class="eyebrow">CONTROLE DO MVP</span><h3>Cenários de demonstração</h3></div><button id="setup" class="primary compact">Preparar demonstração</button></div>
      <p>Selecione um cenário para simular a superfície do fertilizante e gerar uma nova medição imediatamente.</p>
      <div id="scenarios" class="scenario-list"></div>
    </section>

    <section class="workspace">
      <article class="panel twin-panel">
        <div class="panel-heading"><div><span class="eyebrow">VISTA TRIDIMENSIONAL</span><h3>Gêmeo digital do box</h3></div><span id="updated" class="muted">Sem leitura</span></div>
        <canvas id="twinCanvas" aria-label="Representação tridimensional da carga"></canvas>
        <div class="legend"><span>Baixo</span><i></i><span>Alto</span></div>
      </article>

      <article class="panel map-panel">
        <div class="panel-heading"><div><span class="eyebrow">MAPA DE ALTURA</span><h3>Superfície 8×8</h3></div><span class="unit">cm</span></div>
        <div id="grid" class="grid"></div>
      </article>

      <aside class="panel control-panel">
        <div><span class="eyebrow">DIAGNÓSTICO</span><h3>Estado operacional</h3></div>
        <div id="alerts" class="alerts"><p>Nenhum dado disponível.</p></div>
        <button id="capture" class="primary">Capturar novamente</button>
        <button id="calibrate" class="secondary">Calibrar box vazio</button>
      </aside>
    </section>

    <section class="panel history-panel">
      <div class="panel-heading"><div><span class="eyebrow">HISTÓRICO LOCAL</span><h3>Evolução da ocupação</h3></div><span class="muted">Últimas 20 leituras</span></div>
      <canvas id="historyCanvas" aria-label="Histórico de ocupação"></canvas>
    </section>

    <footer><span>HydrogenI · BoxTwin 3D</span><p>MVP para medição automatizada de volume em boxes de fertilizantes.</p></footer>
  </main>
  <script src="{{ url_for('static', filename='app.js') }}"></script>
</body>
</html>

```

### 📄 `boxtwin\templates\login.html`

```html
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#071526"><title>Acesso administrativo | BoxTwin</title><link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body class="auth-page"><main class="auth-card"><div class="brand"><div class="brand-mark">H</div><div><span>HYDROGENI</span><h1>BoxTwin Admin</h1></div></div><p>Acesso restrito aos administradores da operação.</p>{% if error %}<div class="alert danger">{{ error }}</div>{% endif %}<form method="post"><label>Usuário<input name="username" autocomplete="username" required></label><label>Senha<input name="password" type="password" autocomplete="current-password" required></label><button class="primary" type="submit">Entrar</button></form><a href="/">Voltar ao monitoramento</a></main></body></html>

```

### 📄 `data\calibration.json`

```json
{
  "version": 1,
  "empty_distance_grid_mm": [
    [
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0
    ],
    [
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0
    ],
    [
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0
    ],
    [
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0
    ],
    [
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0
    ],
    [
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0
    ],
    [
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0
    ],
    [
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0,
      500.0
    ]
  ]
}
```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\app.py`

```python
from boxtwin import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host=app.config["APP_HOST"], port=app.config["APP_PORT"], debug=app.config["APP_DEBUG"])


```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\ARQUITETURA_V3.md`

```markdown
# Arquitetura BoxTwin v3

## Fluxo operacional

1. O sensor real ou simulado produz uma matriz 8×8.
2. O serviço de volume calcula ocupação, altura, confiança e zonas válidas.
3. O motor de regras identifica capacidade alta, baixa confiança e obstrução.
4. A leitura e as anomalias são gravadas no SQLite.
5. O painel recebe a nova leitura por SSE (`GET /api/stream`).
6. Adaptadores opcionais enviam e-mail ou Twilio com intervalo antirrepetição.
7. O administrador registra ciência e consulta a tratativa no RAG local.

## API preparada para Flutter

| Método | Rota | Uso |
|---|---|---|
| GET | `/api/health` | estado e dimensões do BoxNode |
| GET | `/api/readings/latest` | leitura mais recente |
| GET | `/api/readings/history` | série histórica |
| GET | `/api/stream` | eventos em tempo real |
| GET | `/api/admin/anomalies` | fila protegida de incidentes |
| POST | `/api/admin/anomalies/{id}/acknowledge` | registro de ciência |
| POST | `/api/admin/assistant` | consulta ao RAG |

Para o aplicativo Flutter, a etapa seguinte deverá substituir a sessão web nas rotas móveis por JWT de curta duração, HTTPS obrigatório e armazenamento seguro do token. Não exponha diretamente o Raspberry Pi na internet; utilize um backend central ou VPN/túnel autenticado.

## IA e RAG

A base inicial fica em `boxtwin/knowledge/procedures.json`. O serviço recupera documentos por relevância lexical e devolve as fontes utilizadas. Essa abordagem funciona offline e é adequada ao MVP. Na evolução, o mesmo contrato pode usar embeddings, um banco vetorial e um modelo de linguagem; mantenha sempre as fontes, os limites de decisão e a aprovação humana para ações operacionais.

Quando `XAI_ENABLED=true`, o Grok recebe a pergunta, os dados técnicos da anomalia e somente os procedimentos recuperados. Se houver timeout, indisponibilidade ou chave inválida, a resposta volta automaticamente ao modo `local-rag`.

## Respostas pelo Twilio

- `1 42`: registra ciência da anomalia 42;
- `2 42`: marca a anomalia 42 como em atendimento;
- `3 42`: marca a anomalia 42 como resolvida.

Os webhooks validam `X-Twilio-Signature` quando `TWILIO_VALIDATE_SIGNATURE=true`.

## Segurança antes de publicar

- Alterar `ADMIN_PASSWORD` e `SECRET_KEY`.
- Guardar `.env` fora do GitHub.
- Usar HTTPS e cookies seguros em produção.
- Criar usuários individuais e trilha de auditoria na próxima fase.
- Não permitir que a IA acione máquinas ou descarte alertas automaticamente.
- Usar credenciais de teste do Twilio antes de habilitar mensagens reais.

## Validação

```powershell
pip install -r requirements.txt
pytest -q
python app.py
```

Teste em Android na mesma rede acessando `http://IP_DO_COMPUTADOR:5000`. Em produção, utilize HTTPS.

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\DEPLOY_RAILWAY.md`

```markdown
# Deploy do HydrogenI BoxTwin no Railway

## Fonte

- Repositório: `JuniorDdev/HydrogenI-BoxTwin`
- Branch de homologação: `dev/d-junior`
- Health check: `/api/health`
- Processo: Gunicorn, 1 worker e 8 threads

## Volume persistente obrigatório

Conecte um Railway Volume ao serviço com o caminho:

```text
/app/data
```

O Volume preserva o SQLite, a calibração, destinatários, regras, anomalias e histórico entre deployments.

## Variáveis mínimas

```env
SENSOR_MODE=mock
APP_DEBUG=false
ADMIN_USERNAME=admin
ADMIN_PASSWORD=SUBSTITUA_POR_UMA_SENHA_FORTE
SECRET_KEY=SUBSTITUA_POR_UMA_CHAVE_ALEATORIA_LONGA
BOX_NODE_ID=BOX-DEMO-01
BOX_NAME=Box reduzido HydrogenI
BOX_LENGTH_M=0.60
BOX_WIDTH_M=0.40
BOX_HEIGHT_M=0.50
SAMPLE_INTERVAL_SECONDS=15
CAPACITY_ALERT_PERCENT=85
MIN_CONFIDENCE_PERCENT=70
EMAIL_ENABLED=false
TWILIO_ENABLED=false
XAI_ENABLED=false
TWILIO_VALIDATE_SIGNATURE=true
```

Não defina `PORT`; o Railway fornece essa variável automaticamente.

Depois de gerar o domínio público, acrescente:

```env
PUBLIC_BASE_URL=https://SEU-DOMINIO.up.railway.app
```

Ative Grok, Twilio e e-mail separadamente somente depois de validar painel, login, banco e Volume.

## Verificação

```text
https://SEU-DOMINIO/api/health
https://SEU-DOMINIO/
https://SEU-DOMINIO/simulador
https://SEU-DOMINIO/admin
```

O `manifest.webmanifest` está incluído em `boxtwin/static`, permitindo que o Service Worker conclua o cache inicial da PWA.

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\railway.json`

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120 app:app",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 120,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\README.md`

```markdown
# HydrogenI BoxTwin 3D — MVP demonstrável

Aplicação Flask para demonstrar a medição automatizada do volume de fertilizantes em boxes. Esta versão funciona totalmente sem o sensor físico: um sensor virtual gera uma matriz de profundidade 8×8, e o mesmo fluxo de cálculo usado no modo simulado receberá futuramente as leituras do VL53L8CX.

## O que está pronto

- nove cenários de demonstração: vazio, 25%, 50%, 75%, quase cheio, pilha central, inclinação, carga irregular e obstrução;
- calibração do box vazio;
- matriz de 64 zonas com altura em centímetros;
- cálculo de volume, ocupação, altura média e altura máxima;
- referência conhecida e erro da simulação em pontos percentuais;
- gêmeo digital 3D em Canvas, sem bibliotecas externas;
- histórico local em SQLite;
- alertas de capacidade, confiança e obstrução;
- interface responsiva e operação offline;
- adaptadores separados para modo virtual, VL53L5CX e futuro VL53L8CX.

## Execução no Windows

No terminal do VS Code, dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Acesse `http://127.0.0.1:5000`. A página principal apresenta o projeto. O simulador fica em `/simulador` e a central administrativa autenticada em `/admin`.

Se o PowerShell bloquear a ativação do ambiente, execute uma vez:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Execução no Linux ou Raspberry Pi

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## Como a simulação representa o sensor

O `MockSensor` entrega a mesma estrutura esperada do hardware:

```text
matriz 8×8 de distâncias em milímetros
        ↓
distância do box vazio - distância atual
        ↓
altura da carga em cada célula
        ↓
soma das 64 células × área de cada célula
        ↓
volume total e percentual de ocupação
```

O simulador acrescenta ruído pequeno e determinístico para imitar variação de leitura. O cenário de obstrução retorna zonas inválidas para demonstrar a queda de confiança.

## Configuração da maquete

Edite o arquivo `.env`:

```dotenv
BOX_LENGTH_M=0.60
BOX_WIDTH_M=0.40
BOX_HEIGHT_M=0.50
SENSOR_MODE=mock
```

As três dimensões representam as medidas internas úteis do box. A capacidade é calculada por `comprimento × largura × altura`.

## Integração futura do VL53L8CX

O ponto de integração está em `boxtwin/sensors/vl53l8cx.py`. O adaptador deverá retornar uma lista 8×8 em milímetros e manter `None` nas zonas inválidas. Depois da implementação do driver, altere:

```dotenv
SENSOR_MODE=vl53l8cx
```

O cálculo, banco, API, alertas e painel não precisarão ser reescritos.

## API principal

| Método | Rota | Finalidade |
|---|---|---|
| GET | `/api/health` | Estado do BoxNode e dimensões |
| POST | `/api/demo/setup` | Calibra vazio e inicia a demonstração |
| GET | `/api/demo/scenarios` | Lista cenários disponíveis |
| POST | `/api/demo/scenario/<id>` | Aplica cenário e captura uma leitura |
| POST | `/api/calibration` | Salva a linha de base vazia |
| POST | `/api/readings` | Captura nova leitura |
| GET | `/api/readings/latest` | Retorna a leitura mais recente |
| GET | `/api/readings/history` | Retorna histórico local |
| GET | `/api/admin/summary` | Consolida indicadores do painel administrativo |
| POST | `/api/admin/assistant` | Consulta o assistente técnico com contexto operacional |
| GET | `/admin/reports/operational.pdf` | Gera relatório PDF de leituras e incidentes |

## Testes

```powershell
python -m pytest -q
```

Os testes verificam volume de meia carga, alertas, validação da matriz, inicialização da API, preparação da demonstração e troca de cenários.

## Limite desta versão

Os números no modo `mock` demonstram o método matemático e a experiência operacional, mas não constituem validação de precisão do sensor real. A margem de erro industrial deverá ser medida depois com o VL53L8CX instalado e volumes físicos conhecidos.
# Evolução operacional v3

Além do painel do gêmeo digital, esta versão inclui:

- área administrativa autenticada em `/admin`;
- fila de anomalias com registro de ciência;
- atualização em tempo real via Server-Sent Events (SSE);
- notificações opcionais por SMTP e Twilio (SMS ou WhatsApp Sandbox);
- assistente local com RAG sobre procedimentos em `boxtwin/knowledge/procedures.json`;
- PWA responsiva para Android e contrato JSON reutilizável por um futuro app Flutter.
- cadastro de responsáveis individuais ou equipes;
- regras por anomalia, severidade, canal e tempo de escalonamento;
- Grok pela API da xAI com fallback automático para o RAG local;
- página detalhada de cada incidente, evidências e linha do tempo;
- estados `aberta`, `ciente`, `em atendimento`, `resolvida` e `falso positivo`;
- webhooks Twilio para status de entrega e respostas `1 ID`, `2 ID` ou `3 ID`.
- landing page institucional em `/`, simulador independente em `/simulador` e painel real em `/admin`;
- relatório operacional em PDF com indicadores, leituras recentes, incidentes e nota sobre o modo simulado;
- atalhos de perguntas no assistente e contexto automático da última leitura e das anomalias ativas.

No primeiro acesso local, use `admin` / `HydrogenI@2026` e altere ambos no `.env` antes de qualquer publicação. Para produção, use uma senha forte e uma `SECRET_KEY` aleatória. O RAG atual é deliberadamente local e baseado em recuperação; um provedor de LLM pode ser conectado depois sem mudar a interface administrativa.

Para o Twilio, cadastre os webhooks públicos em `/api/webhooks/twilio/incoming` (mensagens recebidas) e `/api/webhooks/twilio/status` (status). O endereço de `PUBLIC_BASE_URL` deve coincidir exatamente com o domínio HTTPS informado ao Twilio para a validação de assinatura funcionar.

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\requirements.txt`

```
Flask==3.1.1
python-dotenv==1.1.1
numpy==2.2.6
pytest==8.4.1
gunicorn>=23.0,<24.0
reportlab>=4.4,<5.0

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\ROTEIRO_DEMONSTRACAO.md`

```markdown
# Roteiro rápido de demonstração — HydrogenI BoxTwin 3D

## Preparação

1. Execute `python app.py`, apresente `http://127.0.0.1:5000` e abra o simulador pelo botão principal ou por `http://127.0.0.1:5000/simulador`.
2. Clique em **Preparar demonstração**.
3. Deixe aberta a visualização da pilha central.
4. Teste previamente os cenários 50%, irregular, quase cheio e obstrução.

## Demonstração sugerida

1. **Problema:** explique que o estoque atual depende de estimativa visual e atualização manual.
2. **Box vazio:** selecione o cenário vazio e mostre a calibração da referência.
3. **Medição conhecida:** selecione 50% e destaque volume, ocupação e erro contra a referência.
4. **Carga realista:** selecione pilha central ou irregular e mostre por que uma medição em ponto único não representa toda a superfície.
5. **Alerta:** selecione quase cheio e mostre o alerta de capacidade.
6. **Confiabilidade:** selecione obstrução e mostre a redução das zonas válidas.
7. **Evolução:** informe que o sensor virtual será substituído pelo VL53L8CX sem alterar cálculo, banco ou painel.
8. **Operação:** entre em `/admin`, mostre o assistente técnico, a fila de incidentes e baixe o relatório PDF.

## Frase de encerramento

“Hoje demonstramos todo o fluxo de decisão com uma matriz virtual 8×8. Com o VL53L8CX, substituímos apenas a origem dos dados e mantemos o mesmo cálculo volumétrico, histórico, alertas e gêmeo digital.”

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\config.py`

```python
import os
from pathlib import Path

from dotenv import load_dotenv


def _bool(name, default=False):
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def load_config():
    load_dotenv()
    root = Path(__file__).resolve().parent.parent
    return {
        "APP_HOST": os.getenv("APP_HOST", "0.0.0.0"),
        "APP_PORT": int(os.getenv("PORT", os.getenv("APP_PORT", "5000"))),
        "APP_DEBUG": _bool("APP_DEBUG"),
        "SENSOR_MODE": os.getenv("SENSOR_MODE", "mock"),
        "BOX_NODE_ID": os.getenv("BOX_NODE_ID", "BOX-DEMO-01"),
        "BOX_NAME": os.getenv("BOX_NAME", "Box reduzido HydrogenI"),
        "BOX_LENGTH_M": float(os.getenv("BOX_LENGTH_M", "0.60")),
        "BOX_WIDTH_M": float(os.getenv("BOX_WIDTH_M", "0.40")),
        "BOX_HEIGHT_M": float(os.getenv("BOX_HEIGHT_M", "0.50")),
        "SAMPLE_INTERVAL_SECONDS": float(os.getenv("SAMPLE_INTERVAL_SECONDS", "5")),
        "CAPACITY_ALERT_PERCENT": float(os.getenv("CAPACITY_ALERT_PERCENT", "85")),
        "MIN_CONFIDENCE_PERCENT": float(os.getenv("MIN_CONFIDENCE_PERCENT", "70")),
        "SECRET_KEY": os.getenv("SECRET_KEY", "troque-esta-chave-no-ambiente"),
        "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME", "admin"),
        "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD", "HydrogenI@2026"),
        "NOTIFY_COOLDOWN_SECONDS": int(os.getenv("NOTIFY_COOLDOWN_SECONDS", "300")),
        "EMAIL_ENABLED": _bool("EMAIL_ENABLED"),
        "SMTP_HOST": os.getenv("SMTP_HOST", ""),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME", ""),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
        "ALERT_EMAIL_TO": os.getenv("ALERT_EMAIL_TO", ""),
        "TWILIO_ENABLED": _bool("TWILIO_ENABLED"),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "TWILIO_FROM": os.getenv("TWILIO_FROM", ""),
        "TWILIO_TO": os.getenv("TWILIO_TO", ""),
        "PUBLIC_BASE_URL": os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:5000").rstrip("/"),
        "XAI_ENABLED": _bool("XAI_ENABLED"),
        "XAI_API_KEY": os.getenv("XAI_API_KEY", ""),
        "XAI_MODEL": os.getenv("XAI_MODEL", "latest"),
        "XAI_BASE_URL": os.getenv("XAI_BASE_URL", "https://api.x.ai/v1").rstrip("/"),
        "XAI_TIMEOUT_SECONDS": int(os.getenv("XAI_TIMEOUT_SECONDS", "20")),
        "TWILIO_VALIDATE_SIGNATURE": _bool("TWILIO_VALIDATE_SIGNATURE", True),
        "DATABASE_PATH": str(root / os.getenv("DATABASE_PATH", "data/boxtwin.db")),
        "CALIBRATION_PATH": str(root / os.getenv("CALIBRATION_PATH", "data/calibration.json")),
    }

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\database.py`

```python
import json
import sqlite3
from datetime import datetime, timezone


class Database:
    def __init__(self, path):
        self.path = path

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    volume_m3 REAL NOT NULL,
                    capacity_percent REAL NOT NULL,
                    confidence_percent REAL NOT NULL,
                    valid_zones INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    alerts_json TEXT NOT NULL,
                    grid_json TEXT NOT NULL,
                    scenario TEXT,
                    reference_percent REAL,
                    reference_error_points REAL,
                    average_height_m REAL,
                    maximum_height_m REAL,
                    capacity_m3 REAL
                )
            """)
            existing = {row[1] for row in connection.execute("PRAGMA table_info(readings)")}
            migrations = {
                "scenario": "TEXT",
                "reference_percent": "REAL",
                "reference_error_points": "REAL",
                "average_height_m": "REAL",
                "maximum_height_m": "REAL",
                "capacity_m3": "REAL",
            }
            for column, column_type in migrations.items():
                if column not in existing:
                    connection.execute(f"ALTER TABLE readings ADD COLUMN {column} {column_type}")
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    reading_id INTEGER,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    acknowledged_at TEXT,
                    resolution_note TEXT
                );
                CREATE TABLE IF NOT EXISTS notification_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    anomaly_id INTEGER,
                    channel TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT,
                    provider_message_id TEXT,
                    delivery_status TEXT,
                    recipient_id INTEGER
                );
                CREATE TABLE IF NOT EXISTS recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    recipient_type TEXT NOT NULL DEFAULT 'administrator',
                    team_name TEXT,
                    email TEXT,
                    phone TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS notification_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL DEFAULT '*',
                    recipient_id INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    escalation_minutes INTEGER NOT NULL DEFAULT 0,
                    active INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY(recipient_id) REFERENCES recipients(id)
                );
                CREATE TABLE IF NOT EXISTS incident_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anomaly_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    note TEXT
                );
            """)
            notification_columns = {row[1] for row in connection.execute("PRAGMA table_info(notification_log)")}
            for column in ("provider_message_id", "delivery_status", "recipient_id"):
                if column not in notification_columns:
                    connection.execute(f"ALTER TABLE notification_log ADD COLUMN {column} {'INTEGER' if column == 'recipient_id' else 'TEXT'}")

    def save_reading(self, reading):
        created_at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute("""
                INSERT INTO readings (
                    created_at, node_id, volume_m3, capacity_percent,
                    confidence_percent, valid_zones, status, alerts_json, grid_json
                    , scenario, reference_percent, reference_error_points,
                    average_height_m, maximum_height_m, capacity_m3
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                created_at, reading["node_id"], reading["volume_m3"], reading["capacity_percent"],
                reading["confidence_percent"], reading["valid_zones"], reading["status"],
                json.dumps(reading["alerts"]), json.dumps(reading["height_grid_m"]),
                reading.get("scenario"), reading.get("reference_percent"),
                reading.get("reference_error_points"), reading.get("average_height_m"),
                reading.get("maximum_height_m"), reading.get("capacity_m3"),
            ))
            return cursor.lastrowid, created_at

    def latest(self):
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1").fetchone()
        return self._serialize(row) if row else None

    def history(self, limit=50):
        limit = max(1, min(int(limit), 500))
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [self._serialize(row) for row in reversed(rows)]

    def save_anomalies(self, reading_id, alerts):
        created_at = datetime.now(timezone.utc).isoformat()
        records = []
        with self.connect() as connection:
            for alert in alerts:
                cursor = connection.execute(
                    "INSERT INTO anomalies (created_at, reading_id, anomaly_type, severity, message) VALUES (?, ?, ?, ?, ?)",
                    (created_at, reading_id, alert["type"], alert["level"], alert["message"]),
                )
                records.append({"id": cursor.lastrowid, "created_at": created_at, **alert, "status": "open"})
        return records

    def anomalies(self, limit=100, status=None):
        query, params = "SELECT * FROM anomalies", []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(max(1, min(int(limit), 500)))
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(query, params).fetchall()]

    def update_anomaly_status(self, anomaly_id, status, note="", actor="Administrador"):
        allowed = {"open", "acknowledged", "in_progress", "resolved", "false_positive"}
        if status not in allowed:
            raise ValueError("Status de anomalia inválido.")
        at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute(
                "UPDATE anomalies SET status=?, acknowledged_at=COALESCE(acknowledged_at, ?), resolution_note=? WHERE id=?",
                (status, at, note, anomaly_id),
            )
            if cursor.rowcount:
                connection.execute(
                    "INSERT INTO incident_events (anomaly_id, created_at, actor, event_type, note) VALUES (?, ?, ?, ?, ?)",
                    (anomaly_id, at, actor, status, note),
                )
        return cursor.rowcount > 0

    def acknowledge_anomaly(self, anomaly_id, note=""):
        return self.update_anomaly_status(anomaly_id, "acknowledged", note)

    def anomaly_detail(self, anomaly_id):
        with self.connect() as connection:
            anomaly = connection.execute("SELECT * FROM anomalies WHERE id=?", (anomaly_id,)).fetchone()
            if not anomaly:
                return None
            reading = connection.execute("SELECT * FROM readings WHERE id=?", (anomaly["reading_id"],)).fetchone()
            events = connection.execute("SELECT * FROM incident_events WHERE anomaly_id=? ORDER BY id", (anomaly_id,)).fetchall()
            notifications = connection.execute("SELECT * FROM notification_log WHERE anomaly_id=? ORDER BY id DESC", (anomaly_id,)).fetchall()
        return {"anomaly": dict(anomaly), "reading": self._serialize(reading) if reading else None, "events": [dict(x) for x in events], "notifications": [dict(x) for x in notifications]}

    def save_recipient(self, payload):
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO recipients (name, recipient_type, team_name, email, phone, active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (payload["name"], payload.get("recipient_type", "administrator"), payload.get("team_name"), payload.get("email"), payload.get("phone"), int(payload.get("active", True)), now),
            )
            return cursor.lastrowid

    def recipients(self):
        with self.connect() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM recipients ORDER BY active DESC, name").fetchall()]

    def save_rule(self, payload):
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO notification_rules (anomaly_type, severity, recipient_id, channel, escalation_minutes, active) VALUES (?, ?, ?, ?, ?, ?)",
                (payload["anomaly_type"], payload.get("severity", "*"), int(payload["recipient_id"]), payload["channel"], max(0, int(payload.get("escalation_minutes", 0))), int(payload.get("active", True))),
            )
            return cursor.lastrowid

    def rules(self):
        with self.connect() as connection:
            rows = connection.execute("SELECT r.*, p.name recipient_name, p.email, p.phone FROM notification_rules r JOIN recipients p ON p.id=r.recipient_id ORDER BY r.id DESC").fetchall()
        return [dict(row) for row in rows]

    def matching_rules(self, anomaly):
        with self.connect() as connection:
            rows = connection.execute("""SELECT r.*, p.name recipient_name, p.email, p.phone
                FROM notification_rules r JOIN recipients p ON p.id=r.recipient_id
                WHERE r.active=1 AND p.active=1 AND (r.anomaly_type=? OR r.anomaly_type='*')
                AND (r.severity=? OR r.severity='*') ORDER BY r.escalation_minutes""",
                (anomaly["type"], anomaly["level"])).fetchall()
        return [dict(row) for row in rows]

    def due_escalations(self):
        now = datetime.now(timezone.utc)
        due = []
        with self.connect() as connection:
            anomalies = connection.execute("SELECT * FROM anomalies WHERE status IN ('open','acknowledged','in_progress')").fetchall()
            for row in anomalies:
                anomaly = dict(row)
                age_minutes = (now - datetime.fromisoformat(anomaly["created_at"])).total_seconds() / 60
                rules = connection.execute("""SELECT r.*, p.name recipient_name, p.email, p.phone
                    FROM notification_rules r JOIN recipients p ON p.id=r.recipient_id
                    WHERE r.active=1 AND p.active=1 AND r.escalation_minutes>0
                    AND (r.anomaly_type=? OR r.anomaly_type='*') AND (r.severity=? OR r.severity='*')""",
                    (anomaly["anomaly_type"], anomaly["severity"])).fetchall()
                for rule_row in rules:
                    rule = dict(rule_row)
                    already = connection.execute("SELECT 1 FROM notification_log WHERE anomaly_id=? AND recipient_id=? AND channel=?", (anomaly["id"], rule["recipient_id"], rule["channel"])).fetchone()
                    if age_minutes >= rule["escalation_minutes"] and not already:
                        due.append(({"id": anomaly["id"], "type": anomaly["anomaly_type"], "level": anomaly["severity"], "message": anomaly["message"], "created_at": anomaly["created_at"]}, rule))
        return due

    def log_notification(self, anomaly_id, channel, status, detail="", provider_message_id=None, recipient_id=None):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO notification_log (created_at, anomaly_id, channel, status, detail, provider_message_id, delivery_status, recipient_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), anomaly_id, channel, status, detail, provider_message_id, status, recipient_id),
            )

    def update_delivery_status(self, provider_message_id, status, detail=""):
        with self.connect() as connection:
            cursor = connection.execute("UPDATE notification_log SET delivery_status=?, detail=COALESCE(NULLIF(?,''), detail) WHERE provider_message_id=?", (status, detail, provider_message_id))
        return cursor.rowcount

    def notification_history(self, limit=100):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM notification_log ORDER BY id DESC LIMIT ?", (max(1, min(int(limit), 500)),)
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _serialize(row):
        return {
            "id": row["id"], "created_at": row["created_at"], "node_id": row["node_id"],
            "volume_m3": row["volume_m3"], "capacity_percent": row["capacity_percent"],
            "confidence_percent": row["confidence_percent"], "valid_zones": row["valid_zones"],
            "status": row["status"], "alerts": json.loads(row["alerts_json"]),
            "height_grid_m": json.loads(row["grid_json"]),
            "scenario": row["scenario"], "reference_percent": row["reference_percent"],
            "reference_error_points": row["reference_error_points"],
            "average_height_m": row["average_height_m"],
            "maximum_height_m": row["maximum_height_m"], "capacity_m3": row["capacity_m3"],
        }

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\reports.py`

```python
from io import BytesIO
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


NAVY = colors.HexColor("#071526")
BLUE = colors.HexColor("#1769FF")
CYAN = colors.HexColor("#18D4FF")
INK = colors.HexColor("#142238")
MUTED = colors.HexColor("#6F8095")
LINE = colors.HexColor("#DCE5EF")
PAPER = colors.HexColor("#F3F7FB")
GREEN = colors.HexColor("#147D64")
RED = colors.HexColor("#B12F3A")
FORTALEZA = ZoneInfo("America/Fortaleza")


def _local_datetime(value):
    if not value:
        return "-"
    try:
        parsed = __import__("datetime").datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=__import__("datetime").timezone.utc)
        return parsed.astimezone(FORTALEZA).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return str(value)


def _fmt(value, digits=1, suffix=""):
    if value is None:
        return "-"
    return f"{float(value):.{digits}f}{suffix}".replace(".", ",")


def build_operational_report(*, box_name, node_id, sensor_mode, dimensions, readings, anomalies):
    output = BytesIO()
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleBoxTwin", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=NAVY, spaceAfter=5)
    subtitle = ParagraphStyle("SubtitleBoxTwin", parent=styles["Normal"], fontSize=9, leading=13, textColor=MUTED)
    section = ParagraphStyle("SectionBoxTwin", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=NAVY, spaceBefore=10, spaceAfter=8)
    body = ParagraphStyle("BodyBoxTwin", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=INK)
    tiny = ParagraphStyle("TinyBoxTwin", parent=body, fontSize=7, leading=9, textColor=MUTED)
    kpi_label = ParagraphStyle("KpiLabel", parent=body, alignment=TA_CENTER, fontSize=7.5, textColor=MUTED)
    kpi_value = ParagraphStyle("KpiValue", parent=body, alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=NAVY)

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.line(16 * mm, 13 * mm, 194 * mm, 13 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(16 * mm, 8 * mm, f"HydrogenI BoxTwin 3D - {node_id}")
        canvas.drawRightString(194 * mm, 8 * mm, f"Página {document.page}")
        canvas.restoreState()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Relatório operacional HydrogenI BoxTwin 3D",
        author="HydrogenI",
    )

    latest = readings[-1] if readings else None
    active_statuses = {"open", "acknowledged", "in_progress"}
    active_count = sum(item.get("status") in active_statuses for item in anomalies)
    avg_confidence = sum(item.get("confidence_percent", 0) for item in readings) / len(readings) if readings else None
    max_capacity = max((item.get("capacity_percent", 0) for item in readings), default=None)
    generated_at = __import__("datetime").datetime.now(FORTALEZA).strftime("%d/%m/%Y %H:%M")

    story = []
    header = Table([
        [Paragraph("H", ParagraphStyle("Mark", parent=title, alignment=TA_CENTER, textColor=CYAN, fontSize=24)),
         [Paragraph("RELATÓRIO OPERACIONAL", tiny), Paragraph("HydrogenI BoxTwin 3D", title), Paragraph(f"{box_name} | {node_id}", subtitle)]]
    ], colWidths=[18 * mm, 155 * mm])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE), ("LEFTPADDING", (1, 0), (1, 0), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([header, Spacer(1, 6 * mm)])

    status_text = "Sem leituras" if not latest else ("Alerta ativo" if latest.get("status") == "alert" else "Operação normal")
    kpis = [
        ("OCUPAÇÃO ATUAL", _fmt(latest.get("capacity_percent") if latest else None, 1, "%")),
        ("VOLUME ESTIMADO", _fmt(latest.get("volume_m3") if latest else None, 4, " m³")),
        ("CONFIANÇA MÉDIA", _fmt(avg_confidence, 1, "%")),
        ("INCIDENTES ATIVOS", str(active_count)),
    ]
    kpi_table = Table([[Table([[Paragraph(value, kpi_value)], [Paragraph(label, kpi_label)]]) for label, value in kpis]], colWidths=[43.25 * mm] * 4)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PAPER), ("BOX", (0, 0), (-1, -1), .6, LINE),
        ("INNERGRID", (0, 0), (-1, -1), .6, colors.white), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([kpi_table, Spacer(1, 5 * mm)])

    story.append(Paragraph("Resumo da operação", section))
    summary_data = [
        ["Gerado em", generated_at, "Modo do sensor", "Simulado" if sensor_mode == "mock" else "Físico"],
        ["Estado atual", status_text, "Leituras analisadas", str(len(readings))],
        ["Pico de ocupação", _fmt(max_capacity, 1, "%"), "Incidentes registrados", str(len(anomalies))],
        ["Dimensões internas", f"{dimensions['length']} m x {dimensions['width']} m x {dimensions['height']} m", "Última leitura", _local_datetime(latest.get("created_at")) if latest else "-"],
    ]
    summary = Table(summary_data, colWidths=[31 * mm, 55.5 * mm, 31 * mm, 55.5 * mm])
    summary.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK), ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR", (2, 0), (2, -1), MUTED), ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), .45, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary)

    story.append(Paragraph("Leituras recentes", section))
    reading_rows = [["Data e hora", "Cenário", "Volume (m³)", "Ocupação", "Confiança", "Estado"]]
    for item in list(reversed(readings))[:25]:
        reading_rows.append([
            _local_datetime(item.get("created_at")), str(item.get("scenario") or "fisico"), _fmt(item.get("volume_m3"), 4),
            _fmt(item.get("capacity_percent"), 1, "%"), _fmt(item.get("confidence_percent"), 1, "%"),
            "Alerta" if item.get("status") == "alert" else "Normal",
        ])
    if len(reading_rows) == 1:
        reading_rows.append(["Nenhuma leitura disponível", "-", "-", "-", "-", "-"])
    readings_table = Table(reading_rows, repeatRows=1, colWidths=[32 * mm, 29 * mm, 27 * mm, 25 * mm, 27 * mm, 33 * mm])
    readings_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7), ("GRID", (0, 0), (-1, -1), .35, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    story.append(readings_table)

    story.append(PageBreak())
    story.append(Paragraph("Incidentes e anomalias", section))
    status_labels = {"open": "Aberta", "acknowledged": "Ciente", "in_progress": "Em atendimento", "resolved": "Resolvida", "false_positive": "Falso positivo"}
    anomaly_rows = [["ID", "Data e hora", "Tipo", "Severidade", "Situação", "Descrição"]]
    for item in anomalies[:30]:
        anomaly_rows.append([
            f"#{item.get('id')}", _local_datetime(item.get("created_at")), str(item.get("anomaly_type") or "-"),
            "Crítica" if item.get("severity") == "danger" else "Atenção", status_labels.get(item.get("status"), item.get("status") or "-"),
            Paragraph(str(item.get("message") or "-"), tiny),
        ])
    if len(anomaly_rows) == 1:
        anomaly_rows.append(["-", "-", "-", "-", "-", "Nenhuma anomalia registrada"])
    anomaly_table = Table(anomaly_rows, repeatRows=1, colWidths=[11 * mm, 30 * mm, 23 * mm, 22 * mm, 29 * mm, 58 * mm])
    anomaly_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7), ("GRID", (0, 0), (-1, -1), .35, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(anomaly_table)
    story.extend([Spacer(1, 7 * mm), KeepTogether([
        Paragraph("Nota técnica", section),
        Paragraph(
            "Este relatório consolida os registros armazenados pelo BoxTwin. No modo simulado, os valores demonstram o fluxo matemático e operacional do MVP; a precisão industrial deverá ser validada com sensor físico, instalação calibrada e volumes de referência conhecidos.",
            body,
        ),
    ])])

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return output.getvalue()

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\routes.py`

```python
import json
import time
import base64
import hashlib
import hmac
from datetime import datetime, timezone
from functools import wraps
from io import BytesIO

from flask import Blueprint, Response, current_app, jsonify, redirect, render_template, request, send_file, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .reports import build_operational_report

bp = Blueprint("main", __name__)


def runtime():
    return current_app.extensions["boxtwin_runtime"]


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Autenticação administrativa necessária."}), 401
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


@bp.get("/")
def landing():
    return render_template("index.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/simulador")
def simulator():
    return render_template("simulator.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        expected = current_app.config["ADMIN_PASSWORD"]
        password_ok = check_password_hash(expected, password) if expected.startswith(("pbkdf2:", "scrypt:")) else password == expected
        if username == current_app.config["ADMIN_USERNAME"] and password_ok:
            session.clear()
            session["admin_authenticated"] = True
            return redirect(url_for("main.admin"))
        error = "Usuário ou senha inválidos."
    return render_template("login.html", error=error)


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.get("/admin")
@admin_required
def admin():
    return render_template("admin.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/api/admin/summary")
@admin_required
def admin_summary():
    readings = runtime().database.history(100)
    anomaly_items = runtime().database.anomalies(500)
    active_statuses = {"open", "acknowledged", "in_progress"}
    latest_reading = readings[-1] if readings else None
    return jsonify({
        "latest": latest_reading,
        "readings_count": len(readings),
        "active_incidents": sum(item["status"] in active_statuses for item in anomaly_items),
        "resolved_incidents": sum(item["status"] == "resolved" for item in anomaly_items),
        "average_confidence": round(sum(item["confidence_percent"] for item in readings) / len(readings), 1) if readings else None,
        "sensor_mode": current_app.config["SENSOR_MODE"],
    })


@bp.get("/admin/reports/operational.pdf")
@admin_required
def operational_report():
    try:
        limit = max(10, min(int(request.args.get("limit", 50)), 100))
    except ValueError:
        limit = 50
    readings = runtime().database.history(limit)
    anomaly_items = runtime().database.anomalies(limit)
    pdf_bytes = build_operational_report(
        box_name=current_app.config["BOX_NAME"],
        node_id=current_app.config["BOX_NODE_ID"],
        sensor_mode=current_app.config["SENSOR_MODE"],
        dimensions={
            "length": runtime().volume.length_m,
            "width": runtime().volume.width_m,
            "height": runtime().volume.height_m,
        },
        readings=readings,
        anomalies=anomaly_items,
    )
    filename = f"relatorio_boxtwin_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.pdf"
    response = send_file(BytesIO(pdf_bytes), mimetype="application/pdf", as_attachment=True, download_name=filename)
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/admin/anomalies/<int:anomaly_id>")
@admin_required
def anomaly_page(anomaly_id):
    if not runtime().database.anomaly_detail(anomaly_id):
        return "Anomalia não encontrada.", 404
    return render_template("anomaly.html", anomaly_id=anomaly_id)


@bp.get("/api/health")
def health():
    volume = runtime().volume
    return jsonify({
        "status": "online",
        "node_id": current_app.config["BOX_NODE_ID"],
        "box_name": current_app.config["BOX_NAME"],
        "sensor_mode": current_app.config["SENSOR_MODE"],
        "demo_enabled": hasattr(runtime().sensor, "set_scenario"),
        "dimensions_m": {
            "length": volume.length_m,
            "width": volume.width_m,
            "height": volume.height_m,
        },
        "capacity_m3": volume.capacity_m3,
    })


@bp.post("/api/calibration")
def calibrate():
    return jsonify(runtime().calibrate())


@bp.post("/api/readings")
def capture():
    result = runtime().capture()
    return jsonify(result), 409 if result.get("status") == "not_calibrated" else 201


@bp.get("/api/readings/latest")
def latest():
    return jsonify(runtime().database.latest() or {"status": "no_data"})


@bp.get("/api/readings/history")
def history():
    return jsonify(runtime().database.history(request.args.get("limit", 50)))


@bp.get("/api/stream")
def stream():
    def events():
        last_id = None
        while True:
            reading = runtime().database.latest()
            if reading and reading["id"] != last_id:
                last_id = reading["id"]
                yield f"event: reading\ndata: {json.dumps(reading)}\n\n"
            else:
                yield ": keep-alive\n\n"
            time.sleep(2)
    return Response(events(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@bp.get("/api/admin/anomalies")
@admin_required
def anomalies():
    return jsonify(runtime().database.anomalies(request.args.get("limit", 100), request.args.get("status")))


@bp.post("/api/admin/anomalies/<int:anomaly_id>/acknowledge")
@admin_required
def acknowledge(anomaly_id):
    payload = request.get_json(silent=True) or {}
    if not runtime().database.acknowledge_anomaly(anomaly_id, payload.get("note", "")):
        return jsonify({"error": "Anomalia não encontrada."}), 404
    return jsonify({"ok": True, "id": anomaly_id})


@bp.get("/api/admin/anomalies/<int:anomaly_id>")
@admin_required
def anomaly_detail(anomaly_id):
    detail = runtime().database.anomaly_detail(anomaly_id)
    return (jsonify(detail), 200) if detail else (jsonify({"error": "Anomalia não encontrada."}), 404)


@bp.post("/api/admin/anomalies/<int:anomaly_id>/status")
@admin_required
def anomaly_status(anomaly_id):
    payload = request.get_json(silent=True) or {}
    try:
        found = runtime().database.update_anomaly_status(anomaly_id, payload.get("status", ""), payload.get("note", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return (jsonify({"ok": True}), 200) if found else (jsonify({"error": "Anomalia não encontrada."}), 404)


@bp.route("/api/admin/recipients", methods=["GET", "POST"])
@admin_required
def recipients():
    if request.method == "GET":
        return jsonify(runtime().database.recipients())
    payload = request.get_json(silent=True) or {}
    if not str(payload.get("name", "")).strip() or (not payload.get("email") and not payload.get("phone")):
        return jsonify({"error": "Informe nome e ao menos e-mail ou telefone."}), 400
    return jsonify({"id": runtime().database.save_recipient(payload)}), 201


@bp.route("/api/admin/rules", methods=["GET", "POST"])
@admin_required
def rules():
    if request.method == "GET":
        return jsonify(runtime().database.rules())
    payload = request.get_json(silent=True) or {}
    if payload.get("channel") not in {"email", "twilio"} or not payload.get("recipient_id"):
        return jsonify({"error": "Destinatário e canal válido são obrigatórios."}), 400
    payload.setdefault("anomaly_type", "*")
    return jsonify({"id": runtime().database.save_rule(payload)}), 201


@bp.get("/api/admin/notifications")
@admin_required
def notifications():
    return jsonify(runtime().database.notification_history(request.args.get("limit", 100)))


@bp.post("/api/admin/assistant")
@admin_required
def assistant():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"error": "Informe uma pergunta."}), 400
    if len(question) > 1200:
        return jsonify({"error": "A pergunta deve ter no máximo 1.200 caracteres."}), 400
    context = payload.get("context")
    if context is None:
        latest_reading = runtime().database.latest()
        if latest_reading:
            latest_reading = {key: value for key, value in latest_reading.items() if key != "height_grid_m"}
        context = {
            "latest_reading": latest_reading,
            "active_anomalies": runtime().database.anomalies(10, "open"),
        }
    return jsonify(runtime().assistant.answer(question, context))


def valid_twilio_signature():
    if not current_app.config["TWILIO_VALIDATE_SIGNATURE"]:
        return True
    signature = request.headers.get("X-Twilio-Signature", "")
    token = current_app.config["TWILIO_AUTH_TOKEN"]
    if not signature or not token:
        return False
    public_url = current_app.config["PUBLIC_BASE_URL"] + request.path
    material = public_url + "".join(key + value for key in sorted(request.form) for value in request.form.getlist(key))
    expected = base64.b64encode(hmac.new(token.encode(), material.encode(), hashlib.sha1).digest()).decode()
    return hmac.compare_digest(signature, expected)


@bp.post("/api/webhooks/twilio/status")
def twilio_status():
    if not valid_twilio_signature():
        return "Invalid signature", 403
    sid, status = request.form.get("MessageSid", ""), request.form.get("MessageStatus", "")
    runtime().database.update_delivery_status(sid, status, request.form.get("ErrorMessage", ""))
    return "", 204


@bp.post("/api/webhooks/twilio/incoming")
def twilio_incoming():
    if not valid_twilio_signature():
        return "Invalid signature", 403
    parts = request.form.get("Body", "").strip().split()
    action = {"1": "acknowledged", "2": "in_progress", "3": "resolved"}.get(parts[0] if parts else "")
    if not action or len(parts) < 2 or not parts[1].isdigit():
        reply = "Formato inválido. Responda 1 ID para ciência, 2 ID para atendimento ou 3 ID para resolver."
    else:
        anomaly_id = int(parts[1])
        sender = request.form.get("From", "Responsável via Twilio")
        found = runtime().database.update_anomaly_status(anomaly_id, action, "Atualização recebida pelo WhatsApp/SMS.", sender)
        reply = f"BoxTwin #{anomaly_id} atualizado para {action}." if found else "Anomalia não encontrada."
    escaped = reply.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped}</Message></Response>', 200, {"Content-Type": "application/xml"}


@bp.get("/manifest.webmanifest")
def manifest():
    return current_app.send_static_file("manifest.webmanifest")


@bp.get("/service-worker.js")
def service_worker():
    return current_app.send_static_file("service-worker.js")


@bp.post("/api/demo/level/<float:level>")
def demo_level(level):
    sensor = runtime().sensor
    if not hasattr(sensor, "set_level"):
        return jsonify({"error": "Disponível somente no modo mock."}), 400
    sensor.set_level(level)
    return jsonify({"level_percent": sensor.level_percent})


@bp.get("/api/demo/scenarios")
def demo_scenarios():
    sensor = runtime().sensor
    if not hasattr(sensor, "list_scenarios"):
        return jsonify({"error": "Disponível somente no modo simulado."}), 400
    return jsonify({"scenarios": sensor.list_scenarios(), "active": sensor.scenario})


@bp.post("/api/demo/scenario/<scenario>")
def demo_scenario(scenario):
    sensor = runtime().sensor
    if not hasattr(sensor, "set_scenario"):
        return jsonify({"error": "Disponível somente no modo simulado."}), 400
    try:
        sensor.set_scenario(scenario)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    if scenario == "empty":
        runtime().calibrate()
    result = runtime().capture()
    return jsonify(result), 201


@bp.post("/api/demo/setup")
def demo_setup():
    sensor = runtime().sensor
    if not hasattr(sensor, "set_scenario"):
        return jsonify({"error": "Disponível somente no modo simulado."}), 400
    sensor.set_scenario("empty")
    calibration = runtime().calibrate()
    sensor.set_scenario("pile")
    reading = runtime().capture()
    return jsonify({"calibration": calibration, "reading": reading}), 201

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\runtime.py`

```python
import threading
import time

from .sensors import build_sensor
from pathlib import Path

from .services import AlertService, CalibrationService, GrokService, NotificationService, RagService, VolumeService


class BoxTwinRuntime:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.sensor = build_sensor(config["SENSOR_MODE"], config["BOX_HEIGHT_M"])
        self.calibration = CalibrationService(config["CALIBRATION_PATH"])
        self.volume = VolumeService(config["BOX_LENGTH_M"], config["BOX_WIDTH_M"], config["BOX_HEIGHT_M"])
        self.alerts = AlertService(config["CAPACITY_ALERT_PERCENT"], config["MIN_CONFIDENCE_PERCENT"])
        self.notifications = NotificationService(config, database)
        self.rag = RagService(Path(__file__).parent / "knowledge" / "procedures.json")
        self.assistant = GrokService(config, self.rag)
        self._stop = threading.Event()
        self._thread = None

    def calibrate(self):
        grid = self.sensor.read_distance_grid_mm()
        self.calibration.save(grid)
        return {"calibrated": True, "zones": 64, "message": "Linha de base do box vazio salva."}

    def capture(self):
        empty = self.calibration.load()
        if empty is None:
            return {"status": "not_calibrated", "message": "Calibre o box vazio antes de medir."}
        current = self.sensor.read_distance_grid_mm()
        metrics = self.volume.calculate(empty, current)
        reference_percent = getattr(self.sensor, "reference_percent", None)
        reference_error = (
            round(abs(metrics["capacity_percent"] - reference_percent), 2)
            if reference_percent is not None else None
        )
        alerts = self.alerts.evaluate(metrics)
        reading = {
            **metrics,
            "node_id": self.config["BOX_NODE_ID"],
            "sensor_mode": self.config["SENSOR_MODE"],
            "scenario": getattr(self.sensor, "scenario", "physical"),
            "reference_percent": reference_percent,
            "reference_error_points": reference_error,
            "distance_grid_mm": current,
            "status": "alert" if alerts else "normal",
            "alerts": alerts,
        }
        reading_id, created_at = self.database.save_reading(reading)
        anomaly_records = self.database.save_anomalies(reading_id, alerts)
        self.notifications.dispatch(anomaly_records)
        return {**reading, "id": reading_id, "created_at": created_at, "anomaly_ids": [a["id"] for a in anomaly_records]}

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, name="boxtwin-capture", daemon=True)
        self._thread.start()

    def _loop(self):
        while not self._stop.is_set():
            try:
                if self.calibration.load() is not None:
                    self.capture()
            except Exception as exc:
                print(f"[BoxTwin] Falha de leitura: {exc}")
            try:
                self.notifications.dispatch_escalations()
            except Exception as exc:
                print(f"[BoxTwin] Falha no escalonamento: {exc}")
            self._stop.wait(self.config["SAMPLE_INTERVAL_SECONDS"])

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\services.py`

```python
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

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\__init__.py`

```python
from pathlib import Path

from flask import Flask

from .config import load_config
from .database import Database
from .routes import bp
from .runtime import BoxTwinRuntime


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.update(load_config())
    if test_config:
        app.config.update(test_config)
    app.secret_key = app.config["SECRET_KEY"]

    Path(app.config["DATABASE_PATH"]).parent.mkdir(parents=True, exist_ok=True)
    Path(app.config["CALIBRATION_PATH"]).parent.mkdir(parents=True, exist_ok=True)

    database = Database(app.config["DATABASE_PATH"])
    database.initialize()
    runtime = BoxTwinRuntime(app.config, database)
    app.extensions["boxtwin_runtime"] = runtime
    app.register_blueprint(bp)

    if not app.config.get("TESTING"):
        runtime.start()

    return app

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\knowledge\procedures.json`

```json
[
  {"id":"PROC-001","title":"Capacidade próxima do limite","tags":["capacity","capacidade","volume","cheio"],"content":"Confirme a leitura em duas capturas consecutivas, suspenda nova alimentação do box, sinalize a operação e programe retirada ou redistribuição do material."},
  {"id":"PROC-002","title":"Baixa confiança de leitura","tags":["confidence","confiança","sensor","leitura"],"content":"Inspecione fixação e alinhamento do sensor, limpe cuidadosamente a janela óptica, confirme iluminação e vibração e execute nova calibração somente com o box vazio."},
  {"id":"PROC-003","title":"Possível obstrução","tags":["obstruction","obstrução","zonas","poeira"],"content":"Interrompa a medição automática, verifique poeira ou objeto diante do sensor, faça limpeza segura, capture novamente e encaminhe para manutenção se menos de 48 zonas permanecerem válidas."},
  {"id":"PROC-004","title":"Divergência volumétrica","tags":["erro","volume","calibração","divergência"],"content":"Compare as dimensões cadastradas com as dimensões internas reais, valide a linha de base vazia, repita três leituras e registre a diferença contra um volume conhecido."}
]

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\sensors\base.py`

```python
from abc import ABC, abstractmethod


class DepthSensor(ABC):
    @abstractmethod
    def read_distance_grid_mm(self):
        """Retorna uma lista 8×8 de distâncias em milímetros; use None para zona inválida."""


```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\sensors\mock.py`

```python
import math
import random

from .base import DepthSensor


class MockSensor(DepthSensor):
    """Sensor virtual 8x8 para demonstrar o MVP sem hardware físico."""

    SCENARIOS = {
        "empty": {"label": "Box vazio", "description": "Linha de base para calibração."},
        "flat_25": {"label": "Carga uniforme 25%", "description": "Superfície plana em baixa ocupação."},
        "flat_50": {"label": "Carga uniforme 50%", "description": "Meia capacidade com superfície plana."},
        "flat_75": {"label": "Carga uniforme 75%", "description": "Carga elevada e distribuída."},
        "full": {"label": "Box quase cheio", "description": "Ocupação próxima do limite configurado."},
        "pile": {"label": "Pilha central", "description": "Monte de fertilizante com pico no centro."},
        "slope": {"label": "Superfície inclinada", "description": "Carga acumulada em uma das laterais."},
        "irregular": {"label": "Carga irregular", "description": "Ondulações e distribuição não uniforme."},
        "obstruction": {"label": "Sensor parcialmente obstruído", "description": "Simula zonas inválidas e baixa confiança."},
    }

    def __init__(self, box_height_m):
        self.empty_distance_mm = box_height_m * 1000
        self.box_height_m = box_height_m
        self.level_percent = 0.0
        self.scenario = "empty"
        self._capture_count = 0

    def set_level(self, level_percent):
        self.level_percent = max(0.0, min(float(level_percent), 100.0))
        self.scenario = "custom"

    def set_scenario(self, scenario):
        if scenario not in self.SCENARIOS:
            raise ValueError(f"Cenário desconhecido: {scenario}")
        self.scenario = scenario
        presets = {"empty": 0, "flat_25": 25, "flat_50": 50, "flat_75": 75, "full": 92}
        self.level_percent = presets.get(scenario, 0)

    def list_scenarios(self):
        return [{"id": key, **value} for key, value in self.SCENARIOS.items()]

    def _height_ratio(self, row, col):
        if self.scenario in {"empty", "flat_25", "flat_50", "flat_75", "full", "custom"}:
            return self.level_percent / 100

        x = (col - 3.5) / 3.5
        y = (row - 3.5) / 3.5
        radius = math.sqrt(x * x + y * y)
        if self.scenario in {"pile", "obstruction"}:
            return max(0.08, 0.86 * (1 - radius / 1.42))
        if self.scenario == "slope":
            return 0.18 + 0.62 * ((col + row) / 14)
        if self.scenario == "irregular":
            wave = 0.48 + 0.16 * math.sin(col * 1.35) + 0.12 * math.cos(row * 1.7)
            bump = 0.20 * math.exp(-((x + 0.35) ** 2 + (y - 0.2) ** 2) / 0.22)
            return max(0.08, min(wave + bump, 0.88))
        return 0.0

    @property
    def reference_percent(self):
        ratios = [self._height_ratio(row, col) for row in range(8) for col in range(8)]
        return round(sum(ratios) / 64 * 100, 1)

    def read_distance_grid_mm(self):
        self._capture_count += 1
        rng = random.Random(f"{self.scenario}-{self._capture_count}")
        grid = []
        for row in range(8):
            line = []
            for col in range(8):
                if self.scenario == "obstruction" and (
                    (row < 4 and col >= 4) or (row in {4, 5} and col >= 6)
                ):
                    line.append(None)
                    continue
                height_mm = self.empty_distance_mm * self._height_ratio(row, col)
                noise = 0 if self.scenario == "empty" else rng.uniform(-1.8, 1.8)
                line.append(round(max(0, self.empty_distance_mm - height_mm + noise), 2))
            grid.append(line)
        return grid

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\sensors\vl53l5cx.py`

```python
from .base import DepthSensor


class VL53L5CXSensor(DepthSensor):
    """Ponto de integração com o driver físico da placa breakout adquirida."""

    def __init__(self):
        raise RuntimeError(
            "Driver físico ainda não configurado. Use SENSOR_MODE=mock até instalar "
            "o pacote indicado pelo fabricante da placa VL53L5CX."
        )

    def read_distance_grid_mm(self):
        raise NotImplementedError


```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\sensors\vl53l8cx.py`

```python
from .base import DepthSensor


class VL53L8CXSensor(DepthSensor):
    """Adaptador reservado para a placa VL53L8CX física.

    O painel e o cálculo já esperam uma matriz 8x8 em milímetros. Quando a
    placa for adquirida, somente este adaptador precisará receber o driver
    indicado pelo fabricante da breakout.
    """

    def __init__(self):
        raise RuntimeError(
            "Driver do VL53L8CX ainda não configurado. Use SENSOR_MODE=mock "
            "para o Hackathon sem o hardware físico."
        )

    def read_distance_grid_mm(self):
        raise NotImplementedError

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\sensors\__init__.py`

```python
from .mock import MockSensor
from .vl53l5cx import VL53L5CXSensor
from .vl53l8cx import VL53L8CXSensor


def build_sensor(mode, box_height_m):
    if mode == "mock":
        return MockSensor(box_height_m)
    if mode == "vl53l5cx":
        return VL53L5CXSensor()
    if mode == "vl53l8cx":
        return VL53L8CXSensor()
    raise ValueError(f"SENSOR_MODE desconhecido: {mode}")

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\static\admin.js`

```javascript
const $ = id => document.getElementById(id);
const escapeHtml = text => String(text ?? '').replace(/[&<>'"]/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character]));
const statusLabels = {open:'Aberta', acknowledged:'Ciente', in_progress:'Em atendimento', resolved:'Resolvida', false_positive:'Falso positivo'};
const typeLabels = {capacity:'Capacidade', confidence:'Baixa confiança', obstruction:'Obstrução'};
let anomaliesById = new Map();

async function api(url, options = {}) {
  const response = await fetch(url, options);
  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json') ? await response.json() : {};
  if (response.status === 401) {
    location.href = '/login';
    throw new Error('Sessão expirada.');
  }
  if (!response.ok) throw new Error(data.error || 'Não foi possível concluir a operação.');
  return data;
}

function localDate(value) {
  return value ? new Date(value).toLocaleString('pt-BR', {dateStyle:'short', timeStyle:'short'}) : '-';
}

function renderSummary(summary) {
  const latest = summary.latest;
  $('adminOccupancy').textContent = latest ? Number(latest.capacity_percent).toFixed(1) : '-';
  $('adminVolume').textContent = latest ? `${Number(latest.volume_m3).toFixed(4)} m³ estimados` : 'Sem leitura';
  $('adminConfidence').textContent = summary.average_confidence ?? '-';
  $('adminActive').textContent = summary.active_incidents;
  $('adminResolved').textContent = summary.resolved_incidents;
  $('adminSensorMode').textContent = summary.sensor_mode === 'mock' ? 'Virtual' : 'Físico';
  $('adminReadingTime').textContent = latest ? `Leitura: ${localDate(latest.created_at)}` : 'Aguardando telemetria';
}

function renderAnomalies(items) {
  anomaliesById = new Map(items.map(item => [item.id, item]));
  $('anomalyList').innerHTML = items.length ? items.map(item => `
    <article class="incident ${escapeHtml(item.severity)}">
      <div><a href="/admin/anomalies/${item.id}"><b>#${item.id} · ${escapeHtml(item.message)}</b></a><small>${localDate(item.created_at)} · ${escapeHtml(typeLabels[item.anomaly_type] || item.anomaly_type)}</small></div>
      <span class="badge">${escapeHtml(statusLabels[item.status] || item.status)}</span>
      ${item.status === 'open' ? `<button onclick="ack(${item.id})" class="secondary compact">Registrar ciência</button>` : ''}
      <button onclick="askIncident(${item.id})" class="secondary compact">Sugerir tratativa</button>
    </article>`).join('') : '<p class="muted">Nenhuma anomalia registrada.</p>';
}

async function loadAdmin() {
  try {
    const [summary, anomalies, notifications, recipients, rules] = await Promise.all([
      api('/api/admin/summary'), api('/api/admin/anomalies?limit=50'), api('/api/admin/notifications?limit=30'),
      api('/api/admin/recipients'), api('/api/admin/rules')
    ]);
    renderSummary(summary);
    renderAnomalies(anomalies);
    $('notificationList').innerHTML = notifications.length ? notifications.map(item => `<div class="notification-row"><b>${escapeHtml(item.channel)}</b><span>${escapeHtml(item.delivery_status || item.status)}</span><small>${localDate(item.created_at)}</small></div>`).join('') : '<p class="muted">Nenhuma notificação enviada. Os canais externos permanecem opcionais.</p>';
    $('recipientList').innerHTML = recipients.map(item => `<div class="list-row"><b>${escapeHtml(item.name)}</b><span>${escapeHtml(item.team_name || item.recipient_type)}</span><small>${escapeHtml(item.email || item.phone)}</small></div>`).join('') || '<p class="muted">Cadastre o primeiro responsável.</p>';
    $('ruleRecipient').innerHTML = recipients.filter(item => item.active).map(item => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join('');
    $('ruleList').innerHTML = rules.map(item => `<div class="list-row"><b>${escapeHtml(typeLabels[item.anomaly_type] || item.anomaly_type)} → ${escapeHtml(item.recipient_name)}</b><span>${escapeHtml(item.channel)}</span><small>${item.escalation_minutes ? `Após ${item.escalation_minutes} min` : 'Imediata'}</small></div>`).join('') || '<p class="muted">Nenhuma regra cadastrada.</p>';
    $('adminConnection').textContent = 'Online';
  } catch (error) {
    $('adminConnection').textContent = 'Sem conexão';
    $('anomalyList').innerHTML = `<div class="alert danger">${escapeHtml(error.message)}</div>`;
  }
}

async function ack(id) {
  await api(`/api/admin/anomalies/${id}/acknowledge`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({note:'Ciência registrada no painel.'})});
  await loadAdmin();
}

async function askIncident(id) {
  const item = anomaliesById.get(id);
  if (!item) return;
  const question = `Anomalia #${id}: ${item.message}. Qual é a tratativa recomendada e quais verificações devem ser feitas?`;
  $('assistantQuestion').value = question;
  updateAssistantCount();
  await queryAssistant(question);
}

async function queryAssistant(question) {
  const cleanQuestion = String(question || '').trim();
  if (!cleanQuestion) return;
  $('assistantAnswer').textContent = 'Consultando procedimentos e contexto operacional...';
  try {
    const result = await api('/api/admin/assistant', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question:cleanQuestion})});
    const sources = result.sources.map(source => escapeHtml(`${source.id} - ${source.title}`)).join('; ') || 'nenhuma fonte correspondente';
    $('assistantAnswer').innerHTML = `<p>${escapeHtml(result.answer)}</p><small>Fontes: ${sources} · Modo: ${escapeHtml(result.mode)}</small>`;
  } catch (error) {
    $('assistantAnswer').innerHTML = `<div class="alert danger">${escapeHtml(error.message)}</div>`;
  }
}

function updateAssistantCount() {
  $('assistantCount').textContent = `${$('assistantQuestion').value.length}/1200`;
}

$('assistantForm').addEventListener('submit', event => { event.preventDefault(); queryAssistant($('assistantQuestion').value); });
$('assistantQuestion').addEventListener('input', updateAssistantCount);
document.querySelectorAll('.quick-prompt').forEach(button => button.addEventListener('click', () => {
  $('assistantQuestion').value = button.dataset.prompt;
  updateAssistantCount();
  queryAssistant(button.dataset.prompt);
}));
$('refreshAdmin').addEventListener('click', loadAdmin);
$('recipientForm').addEventListener('submit', async event => {
  event.preventDefault();
  await api('/api/admin/recipients', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name:$('recipientName').value, recipient_type:$('recipientType').value, team_name:$('recipientTeam').value, email:$('recipientEmail').value, phone:$('recipientPhone').value})});
  event.target.reset();
  await loadAdmin();
});
$('ruleForm').addEventListener('submit', async event => {
  event.preventDefault();
  await api('/api/admin/rules', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({anomaly_type:$('ruleType').value, severity:$('ruleSeverity').value, recipient_id:$('ruleRecipient').value, channel:$('ruleChannel').value, escalation_minutes:$('ruleDelay').value})});
  await loadAdmin();
});

const stream = new EventSource('/api/stream');
stream.addEventListener('reading', () => loadAdmin());
stream.onerror = () => { $('adminConnection').textContent = 'Reconectando...'; };
stream.onopen = () => { $('adminConnection').textContent = 'Online'; };
loadAdmin();

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\static\anomaly.js`

```javascript
const $=id=>document.getElementById(id);let detail;
const safe=v=>String(v??'—').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
async function api(url,options={}){const r=await fetch(url,options);const d=await r.json();if(r.status===401){location.href='/login';throw new Error('Sessão expirada');}if(!r.ok)throw new Error(d.error||'Falha');return d;}
function renderGrid(reading){const box=$('incidentGrid');box.innerHTML='';(reading?.height_grid_m||[]).flat().forEach(v=>{const c=document.createElement('div');c.className='cell';c.textContent=(v*100).toFixed(1);c.style.opacity=.45+Math.min(1,v/(reading.maximum_height_m||1))*.55;box.appendChild(c);});}
async function load(){detail=await api(`/api/admin/anomalies/${window.ANOMALY_ID}`);const a=detail.anomaly,r=detail.reading;$('incidentSummary').innerHTML=`<div><span class="eyebrow">${safe(a.severity)} · ${safe(a.status)}</span><h2>${safe(a.message)}</h2><p>${new Date(a.created_at).toLocaleString('pt-BR')} · ${safe(r?.node_id)}</p></div>`;$('readingDetail').innerHTML=`<div><small>Ocupação</small><b>${r?.capacity_percent??'—'}%</b></div><div><small>Volume</small><b>${r?.volume_m3??'—'} m³</b></div><div><small>Confiança</small><b>${r?.confidence_percent??'—'}%</b></div><div><small>Zonas válidas</small><b>${r?.valid_zones??'—'}/64</b></div>`;renderGrid(r);$('timeline').innerHTML=[{created_at:a.created_at,actor:'BoxTwin',event_type:'detected',note:a.message},...detail.events].map(e=>`<div class="timeline-event"><b>${safe(e.event_type)}</b><span>${safe(e.actor)}</span><small>${new Date(e.created_at).toLocaleString('pt-BR')}</small><p>${safe(e.note)}</p></div>`).join('');}
$('statusForm').onsubmit=async e=>{e.preventDefault();await api(`/api/admin/anomalies/${window.ANOMALY_ID}/status`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:$('incidentStatus').value,note:$('incidentNote').value})});await load();};
$('suggestTreatment').onclick=async()=>{const a=detail.anomaly,r=detail.reading;$('treatment').textContent='Analisando…';const result=await api('/api/admin/assistant',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:`Como tratar ${a.anomaly_type}: ${a.message}?`,context:r})});$('treatment').innerHTML=`<p>${safe(result.answer)}</p><small>Modo: ${safe(result.mode)} · Fontes: ${result.sources.map(s=>safe(s.id)).join(', ')}</small>`;};load();

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\static\app.js`

```javascript
const $ = id => document.getElementById(id);
const state = { latest: null, health: null, activeScenario: null };

function fmt(value, digits = 1) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(digits) : '—';
}

function colorFor(value, max) {
  const ratio = Math.max(0, Math.min(1, value / Math.max(max, .001)));
  const stops = [[18,58,112],[20,151,218],[24,213,255],[255,181,71]];
  const scaled = ratio * (stops.length - 1);
  const index = Math.min(stops.length - 2, Math.floor(scaled));
  const part = scaled - index;
  const rgb = stops[index].map((v, i) => Math.round(v + (stops[index + 1][i] - v) * part));
  return `rgb(${rgb.join(',')})`;
}

function renderGrid(data) {
  const grid = $('grid');
  grid.innerHTML = '';
  const values = data.height_grid_m.flat();
  const max = Math.max(...values, .001);
  values.forEach(value => {
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.style.background = colorFor(value, max);
    cell.textContent = (value * 100).toFixed(1);
    cell.title = `Altura: ${(value * 100).toFixed(2)} cm`;
    grid.appendChild(cell);
  });
}

function sizeCanvas(canvas) {
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(1, Math.round(rect.width * ratio));
  canvas.height = Math.max(1, Math.round(rect.height * ratio));
  const context = canvas.getContext('2d');
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  return { context, width: rect.width, height: rect.height };
}

function drawTwin(grid) {
  const canvas = $('twinCanvas');
  const { context: ctx, width, height } = sizeCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  const maxValue = Math.max(...grid.flat(), .001);
  const centerX = width * .50, originY = height * .76;
  const scaleX = Math.min(width / 19, 31), scaleY = scaleX * .48, scaleZ = height * 1.22;
  const project = (row, col, z = 0) => ({
    x: centerX + (col - row) * scaleX,
    y: originY + (col + row - 7) * scaleY - z * scaleZ
  });

  ctx.strokeStyle = '#78b8df55'; ctx.lineWidth = 1;
  const base = [project(0,0), project(0,7), project(7,7), project(7,0)];
  ctx.beginPath(); base.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y)); ctx.closePath();
  ctx.fillStyle = '#0a2238'; ctx.fill(); ctx.stroke();

  for (let sum = 0; sum <= 12; sum++) {
    for (let row = 0; row < 7; row++) {
      const col = sum - row;
      if (col < 0 || col >= 7) continue;
      const corners = [
        [row,col,grid[row][col]], [row,col+1,grid[row][col+1]],
        [row+1,col+1,grid[row+1][col+1]], [row+1,col,grid[row+1][col]]
      ].map(([r,c,z]) => project(r,c,z));
      const avg = (grid[row][col] + grid[row][col+1] + grid[row+1][col+1] + grid[row+1][col]) / 4;
      ctx.beginPath(); corners.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y)); ctx.closePath();
      ctx.fillStyle = colorFor(avg, maxValue); ctx.globalAlpha = .88; ctx.fill();
      ctx.globalAlpha = 1; ctx.strokeStyle = '#d8f5ff55'; ctx.stroke();
    }
  }

  ctx.strokeStyle = '#9bdcffaa'; ctx.lineWidth = 1.2;
  [[0,0],[0,7],[7,7],[7,0]].forEach(([r,c]) => {
    const bottom = project(r,c,0), top = project(r,c,state.health?.dimensions_m?.height || .5);
    ctx.beginPath(); ctx.moveTo(bottom.x,bottom.y); ctx.lineTo(top.x,top.y); ctx.stroke();
  });
  ctx.fillStyle = '#b8d4e8'; ctx.font = '11px Segoe UI';
  ctx.fillText('Superfície estimada da carga', 15, 22);
}

function drawHistory(items) {
  const canvas = $('historyCanvas');
  const { context: ctx, width, height } = sizeCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  const pad = { left: 38, right: 14, top: 15, bottom: 24 };
  const w = width - pad.left - pad.right, h = height - pad.top - pad.bottom;
  ctx.font = '10px Segoe UI'; ctx.fillStyle = '#708196'; ctx.strokeStyle = '#dce5ef'; ctx.lineWidth = 1;
  [0,25,50,75,100].forEach(value => {
    const y = pad.top + h * (1 - value / 100);
    ctx.beginPath(); ctx.moveTo(pad.left,y); ctx.lineTo(width-pad.right,y); ctx.stroke();
    ctx.fillText(`${value}%`, 5, y + 3);
  });
  if (!items.length) return;
  const points = items.map((item,index) => ({
    x: pad.left + (items.length === 1 ? w / 2 : index * w / (items.length - 1)),
    y: pad.top + h * (1 - Math.min(100,item.capacity_percent) / 100)
  }));
  const gradient = ctx.createLinearGradient(0,pad.top,0,pad.top+h);
  gradient.addColorStop(0,'rgba(23,105,255,.30)'); gradient.addColorStop(1,'rgba(23,105,255,0)');
  ctx.beginPath(); points.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y));
  ctx.lineTo(points.at(-1).x,pad.top+h); ctx.lineTo(points[0].x,pad.top+h); ctx.closePath(); ctx.fillStyle=gradient; ctx.fill();
  ctx.beginPath(); points.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y));
  ctx.strokeStyle='#1769ff'; ctx.lineWidth=2.5; ctx.stroke();
  points.forEach(p => {ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fillStyle='#fff';ctx.fill();ctx.strokeStyle='#1769ff';ctx.stroke();});
}

function setActiveScenario(id) {
  state.activeScenario = id;
  document.querySelectorAll('.scenario').forEach(button => button.classList.toggle('active', button.dataset.id === id));
}

function render(data) {
  if (!data || !data.id) return;
  state.latest = data;
  $('volume').textContent = fmt(data.volume_m3, 4);
  $('capacity').textContent = fmt(data.capacity_percent, 1);
  $('capacityBar').style.width = `${Math.min(100, data.capacity_percent)}%`;
  $('avgHeight').textContent = fmt((data.average_height_m || 0) * 100, 1);
  $('maxHeight').textContent = `Pico: ${fmt((data.maximum_height_m || 0) * 100, 1)} cm`;
  $('confidence').textContent = fmt(data.confidence_percent, 1);
  $('zones').textContent = data.valid_zones;
  $('referenceError').textContent = fmt(data.reference_error_points, 2);
  $('referenceValue').textContent = data.reference_percent == null ? 'Referência indisponível no sensor real' : `Referência: ${fmt(data.reference_percent,1)}%`;
  $('updated').textContent = `Atualizado ${new Date(data.created_at).toLocaleString('pt-BR')}`;
  setActiveScenario(data.scenario);
  renderGrid(data); drawTwin(data.height_grid_m);
  $('alerts').innerHTML = data.alerts.length
    ? data.alerts.map(alert => `<div class="alert ${alert.level}">${alert.message}</div>`).join('')
    : '<div class="alert ok">Operação normal. Nenhum alerta ativo.</div>';
}

async function request(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || data.message || 'Falha na operação.');
  return data;
}

async function loadHistory() {
  const items = await request('/api/readings/history?limit=20');
  drawHistory(items);
}

async function chooseScenario(id, button) {
  const buttons = document.querySelectorAll('.scenario'); buttons.forEach(item => item.disabled = true);
  try { render(await request(`/api/demo/scenario/${id}`, {method:'POST'})); await loadHistory(); }
  catch (error) { alert(error.message); }
  finally { buttons.forEach(item => item.disabled = false); }
}

async function loadScenarios() {
  if (!state.health.demo_enabled) { $('demoPanel').hidden = true; return; }
  const data = await request('/api/demo/scenarios');
  $('scenarios').innerHTML = '';
  data.scenarios.forEach(item => {
    const button = document.createElement('button'); button.className='scenario'; button.dataset.id=item.id;
    button.textContent=item.label; button.title=item.description; button.onclick=()=>chooseScenario(item.id,button);
    $('scenarios').appendChild(button);
  });
  setActiveScenario(data.active);
}

async function initialize() {
  try {
    state.health = await request('/api/health');
    $('connection').textContent='● BoxNode online'; $('connection').classList.add('online');
    const d=state.health.dimensions_m;
    $('boxCapacity').textContent=`${fmt(state.health.capacity_m3,3)} m³`;
    $('boxDimensions').textContent=`${d.length} m × ${d.width} m × ${d.height} m`;
    if (!state.health.demo_enabled) { $('modeBadge').textContent='SENSOR FÍSICO'; $('modeBadge').classList.remove('demo'); }
    await loadScenarios();
    const latest = await request('/api/readings/latest');
    if (latest.status === 'no_data' && state.health.demo_enabled) {
      const setup = await request('/api/demo/setup',{method:'POST'}); render(setup.reading);
    } else render(latest);
    await loadHistory();
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/service-worker.js').catch(()=>{});
    const stream = new EventSource('/api/stream');
    stream.addEventListener('reading', event => { const reading=JSON.parse(event.data); if(reading.id!==state.latest?.id){render(reading);loadHistory().catch(()=>{});} });
    stream.onerror=()=>{$('connection').textContent='● Reconectando…';};
    stream.onopen=()=>{$('connection').textContent='● BoxNode online';};
  } catch (error) {
    $('connection').textContent='● Sem conexão'; $('connection').classList.remove('online');
    $('alerts').innerHTML=`<div class="alert danger">${error.message}</div>`;
  }
}

$('setup').onclick = async () => { const data=await request('/api/demo/setup',{method:'POST'});render(data.reading);await loadHistory(); };
$('capture').onclick = async () => { try{render(await request('/api/readings',{method:'POST'}));await loadHistory();}catch(error){alert(error.message);} };
$('calibrate').onclick = async () => {
  if (!confirm('A calibração definirá o box como vazio. Deseja continuar?')) return;
  try {
    if (state.health.demo_enabled) render(await request('/api/demo/scenario/empty',{method:'POST'}));
    else { await request('/api/calibration',{method:'POST'}); alert('Calibração salva.'); }
    await loadHistory();
  } catch(error){alert(error.message);}
};
window.addEventListener('resize',()=>{if(state.latest)drawTwin(state.latest.height_grid_m);loadHistory().catch(()=>{});});
initialize();

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\static\landing.js`

```javascript
const landingEl = id => document.getElementById(id);

function landingFormat(value, digits = 1) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(digits).replace('.', ',') : '--';
}

function previewColor(value, max) {
  const ratio = Math.max(0, Math.min(1, value / Math.max(max, 0.001)));
  const hue = 210 - ratio * 165;
  return `hsl(${hue} 88% ${42 + ratio * 12}%)`;
}

function renderPreviewGrid(grid) {
  const values = grid?.flat?.() || Array.from({length: 64}, (_, index) => .05 + Math.sin(index / 5) * .025);
  const max = Math.max(...values.filter(Number.isFinite), .001);
  landingEl('landingGrid').innerHTML = values.map((value, index) => {
    const safe = Number.isFinite(Number(value)) ? Number(value) : 0;
    return `<i style="--delay:${index * 8}ms;background:${previewColor(safe, max)};opacity:${.35 + safe / max * .65}"></i>`;
  }).join('');
}

async function loadLandingTelemetry() {
  renderPreviewGrid();
  try {
    const [healthResponse, latestResponse] = await Promise.all([fetch('/api/health'), fetch('/api/readings/latest')]);
    const health = await healthResponse.json();
    const latest = await latestResponse.json();
    landingEl('landingStatus').textContent = health.status === 'online' ? 'BoxNode online' : 'Indisponível';
    landingEl('landingStatus').classList.toggle('online', health.status === 'online');
    if (latest.id) {
      landingEl('landingOccupancy').textContent = `${landingFormat(latest.capacity_percent)}%`;
      landingEl('landingConfidence').textContent = `${landingFormat(latest.confidence_percent)}%`;
      landingEl('landingVolume').textContent = `${landingFormat(latest.volume_m3, 4)} m³`;
      landingEl('landingReadingState').textContent = latest.status === 'alert' ? 'Leitura com alerta operacional.' : 'Leitura dentro dos limites.';
      renderPreviewGrid(latest.height_grid_m);
    } else {
      landingEl('landingReadingState').textContent = 'BoxNode online, ainda sem leitura registrada.';
    }
  } catch (error) {
    landingEl('landingStatus').textContent = 'Modo de apresentação';
    landingEl('landingReadingState').textContent = 'Abra o simulador para gerar telemetria.';
  }
}

const menuToggle = landingEl('menuToggle');
const landingMenu = landingEl('landingMenu');
menuToggle.addEventListener('click', () => {
  const open = landingMenu.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(open));
});
landingMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
  landingMenu.classList.remove('open');
  menuToggle.setAttribute('aria-expanded', 'false');
}));

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, {threshold: .12});
document.querySelectorAll('.reveal').forEach(element => observer.observe(element));
loadLandingTelemetry();

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\static\service-worker.js`

```javascript
const CACHE='boxtwin-v6';const ASSETS=['/','/simulador','/static/style.css','/static/landing.js','/static/app.js','/manifest.webmanifest'];self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key))))));self.addEventListener('fetch',e=>{if(e.request.method==='GET'&&!e.request.url.includes('/api/'))e.respondWith(fetch(e.request).then(r=>{const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));return r;}).catch(()=>caches.match(e.request)));});

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\static\style.css`

```css
:root{--navy:#061426;--navy2:#0b2542;--blue:#1769ff;--cyan:#18d4ff;--green:#1fd19b;--amber:#ffb547;--red:#ef5b67;--paper:#eef3f8;--ink:#142238;--muted:#6f8095;--line:#dce5ef;--card:#fff}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,"Segoe UI",Arial,sans-serif}.topbar{display:flex;justify-content:space-between;align-items:center;padding:23px max(4vw,24px);color:white;background:radial-gradient(circle at 80% 0,#194c7b 0,transparent 32%),linear-gradient(125deg,var(--navy),#0a2038);border-bottom:1px solid #ffffff17}.brand,.status-group{display:flex;align-items:center;gap:13px}.brand-mark{display:grid;place-items:center;width:46px;height:46px;border:1px solid #36c8ff80;border-radius:14px;background:#0a3153;color:var(--cyan);font-size:25px;font-weight:900}.brand span,.eyebrow{font-size:10px;letter-spacing:.17em;font-weight:900;color:#1285ce}.brand span{color:var(--cyan)}h1{margin:3px 0 1px;font-size:23px}.brand p{margin:0;color:#aebfd1;font-size:12px}.badge{padding:8px 11px;border:1px solid #ffffff1f;border-radius:99px;background:#21374e;font-size:10px;letter-spacing:.05em}.badge.demo{color:#8de9ff;background:#0a405a}.badge.online{color:#65e4b9;background:#123f3c}main{width:min(1320px,94vw);margin:24px auto}.hero{display:grid;grid-template-columns:1fr auto;align-items:center;gap:30px;margin-bottom:18px;padding:24px 27px;border-radius:19px;color:white;background:linear-gradient(120deg,#0a2542,#103b61);box-shadow:0 16px 38px #09243d1c}.hero h2{margin:5px 0 7px;font-size:clamp(25px,3vw,38px)}.hero p{max-width:760px;margin:0;color:#b9c9d8;line-height:1.55}.box-spec{min-width:220px;padding:18px;border-left:1px solid #ffffff20}.box-spec span,.box-spec small{display:block;color:#adbed0}.box-spec strong{display:block;margin:5px 0;font-size:30px}.metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:13px}.metrics article,.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:0 10px 30px #1029440a}.metrics article{padding:18px}.metrics small{display:block;color:var(--muted);font-weight:650}.metrics strong{font-size:31px;margin-right:4px}.metrics span,.metrics em{color:var(--muted)}.metrics em{display:block;margin-top:5px;font-size:11px;font-style:normal}.meter{height:5px;margin-top:9px;overflow:hidden;border-radius:10px;background:#e7eef6}.meter i{display:block;width:0;height:100%;border-radius:10px;background:linear-gradient(90deg,var(--green),var(--amber),var(--red));transition:width .4s}.panel{padding:20px}.demo-panel{margin-top:15px;border-color:#bdeafa;background:linear-gradient(115deg,#f9fdff,#effaff)}.demo-panel>p{margin:5px 0 13px;color:var(--muted)}.panel-heading{display:flex;justify-content:space-between;align-items:center;gap:12px}.panel h3{margin:3px 0 12px;font-size:17px}.scenario-list{display:flex;flex-wrap:wrap;gap:8px}.scenario{width:auto;margin:0;padding:9px 12px;border:1px solid #c9d9e9;background:white;color:#31506d}.scenario:hover,.scenario.active{border-color:var(--blue);background:#e9f1ff;color:#0755cd}.workspace{display:grid;grid-template-columns:1.45fr 1fr .72fr;gap:15px;margin-top:15px}.twin-panel canvas{display:block;width:100%;height:330px;border-radius:12px;background:linear-gradient(#071a2e,#0b2d4a)}.map-panel{min-width:0}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:5px;aspect-ratio:1}.cell{display:grid;place-items:center;min-width:0;border-radius:6px;color:#fff;font-size:9px;font-weight:800;background:#cbd8e7;transition:transform .2s}.cell:hover{transform:scale(1.06)}.unit,.muted{font-size:11px;color:var(--muted)}.legend{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:10px;color:var(--muted);font-size:10px}.legend i{width:150px;height:7px;border-radius:8px;background:linear-gradient(90deg,#123a70,#16d5ff,#ffb547)}.alerts{min-height:180px}.alerts p{color:var(--muted);line-height:1.5}.alert{padding:10px;margin:8px 0;border-radius:9px;background:#fff3d9;border-left:4px solid var(--amber);font-size:12px}.alert.danger{background:#ffe7ea;border-color:var(--red)}.alert.ok{background:#e4faf3;border-color:var(--green)}button{width:100%;padding:12px;margin-top:9px;border:0;border-radius:9px;font-weight:800;cursor:pointer;transition:filter .2s,transform .2s}button:hover{filter:brightness(.97);transform:translateY(-1px)}button:disabled{opacity:.55;cursor:wait}.primary{background:var(--blue);color:white}.secondary{background:#e7eef8;color:#174775}.compact{width:auto;margin:0;padding:10px 14px}.history-panel{margin-top:15px}.history-panel canvas{display:block;width:100%;height:170px}footer{display:flex;justify-content:space-between;align-items:center;padding:25px 4px;color:var(--muted);font-size:12px}footer span{font-weight:900;color:#31506d}@media(max-width:1100px){.metrics{grid-template-columns:repeat(3,1fr)}.workspace{grid-template-columns:1fr 1fr}.control-panel{grid-column:1/-1}.alerts{min-height:0}}@media(max-width:720px){.topbar,.hero,footer{align-items:flex-start;flex-direction:column}.status-group{flex-wrap:wrap}.hero{grid-template-columns:1fr}.box-spec{padding:12px 0 0;border-left:0;border-top:1px solid #ffffff20}.metrics{grid-template-columns:repeat(2,1fr)}.workspace{grid-template-columns:1fr}.control-panel{grid-column:auto}.panel-heading{align-items:flex-start}.demo-panel .panel-heading{flex-direction:column}.compact{width:100%}.twin-panel canvas{height:275px}.metrics strong{font-size:27px}}
/* Administração, autenticação e experiência móvel */
.topbar a{color:inherit;text-decoration:none}.topbar form{margin:0}.topbar button.badge{font:inherit;cursor:pointer}
.auth-page{min-height:100vh;display:grid;place-items:center;background:radial-gradient(circle at top,#12395b,#06111f 55%);padding:20px}
.auth-card{width:min(420px,100%);background:#fff;color:#122234;padding:32px;border-radius:22px;box-shadow:0 25px 70px #0008}.auth-card form{display:grid;gap:16px;margin:24px 0}.auth-card label{display:grid;gap:7px;font-weight:700}.auth-card input,.assistant-panel textarea{width:100%;box-sizing:border-box;border:1px solid #cad7e5;border-radius:10px;padding:12px;font:inherit}.auth-card .brand span,.auth-card .brand h1{color:#102c46}.auth-card a{color:#1769ff}
.admin-grid{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(300px,.85fr);gap:18px;margin-bottom:18px}.incident-list{display:grid;gap:10px}.incident{display:grid;grid-template-columns:1fr auto auto auto;align-items:center;gap:10px;padding:14px;border:1px solid #dce6ef;border-left:4px solid #f0a928;border-radius:10px}.incident.danger{border-left-color:#dc3545}.incident small{display:block;color:#708196;margin-top:4px}.assistant-panel form{display:grid;gap:10px}.assistant-answer{min-height:100px;background:#eef6fc;border-radius:12px;padding:14px;margin:14px 0}.notification-list{display:grid;gap:8px}.notification-row{display:grid;grid-template-columns:1fr 1fr 2fr;gap:12px;padding:10px;border-bottom:1px solid #dce6ef}
@media(max-width:760px){.topbar{align-items:flex-start;gap:12px}.status-group{flex-wrap:wrap}.admin-grid{grid-template-columns:1fr}.incident{grid-template-columns:1fr 1fr}.incident>div{grid-column:1/-1}.notification-row{grid-template-columns:1fr 1fr}.notification-row small{grid-column:1/-1}.auth-card{padding:24px}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.workspace{display:block}.workspace>*{margin-bottom:16px}.hero{display:block}.box-spec{margin-top:16px}.scenario-list{display:grid;grid-template-columns:1fr 1fr}}
@media(max-width:430px){.metrics{grid-template-columns:1fr}.scenario-list{grid-template-columns:1fr}.topbar{padding:14px}.brand h1{font-size:1.15rem}main{padding:12px}.panel{padding:14px}.incident{grid-template-columns:1fr}.incident>*{grid-column:1/-1}}
.inline-form,.stack-form{display:grid;gap:10px;margin:14px 0}.inline-form{grid-template-columns:repeat(2,minmax(0,1fr))}.inline-form input,.inline-form select,.stack-form select,.stack-form textarea{border:1px solid #cad7e5;border-radius:9px;padding:10px;font:inherit;background:#fff}.inline-form button{grid-column:1/-1}.compact-list{display:grid;gap:7px}.list-row{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:10px;padding:10px;border-bottom:1px solid #dce6ef}.incident a{color:inherit;text-decoration:none}.incident a:hover{text-decoration:underline}.detail-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:15px 0}.detail-grid>div{background:#eef6fc;padding:12px;border-radius:10px}.detail-grid small,.detail-grid b{display:block}.timeline{border-left:2px solid #87b7d8;margin-left:8px;padding-left:20px}.timeline-event{position:relative;padding:0 0 20px}.timeline-event:before{content:'';position:absolute;width:10px;height:10px;border-radius:50%;background:#1769ff;left:-26px;top:4px}.timeline-event span,.timeline-event small{display:block;color:#708196}.timeline-event p{margin:.4rem 0}.management-grid{margin-top:18px}
@media(max-width:760px){.inline-form,.list-row,.detail-grid{grid-template-columns:1fr}.inline-form button{grid-column:auto}}

/* Landing page */
.landing-page{background:#f5f8fb;color:#0d2136;overflow-x:hidden}.landing-page a{text-decoration:none;color:inherit}.landing-nav{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;width:min(1180px,calc(100% - 40px));margin:0 auto;padding:17px 0;background:#f5f8fbeF;backdrop-filter:blur(16px)}.landing-brand{display:flex;align-items:center;gap:11px}.landing-brand>span{display:grid;place-items:center;width:39px;height:39px;border-radius:12px;background:#071526;color:#18d4ff;font-size:21px;font-weight:950;box-shadow:inset 0 0 0 1px #4adfff35}.landing-brand div{display:grid}.landing-brand b{font-size:12px;letter-spacing:.16em}.landing-brand small{font-size:8px;letter-spacing:.22em;color:#687d91;margin-top:2px}.landing-menu{display:flex;align-items:center;gap:24px;font-size:12px;font-weight:750}.landing-menu>a{transition:color .2s,transform .2s}.landing-menu>a:hover{color:#1769ff;transform:translateY(-1px)}.landing-menu .nav-secondary,.landing-menu .nav-primary{padding:10px 15px;border-radius:10px}.landing-menu .nav-secondary{border:1px solid #cad8e5}.landing-menu .nav-primary{background:#1769ff;color:#fff;box-shadow:0 10px 22px #1769ff2a}.menu-toggle{display:none;width:auto;margin:0;padding:9px 12px;background:#071526;color:#fff}.landing-main{width:100%;margin:0}.landing-hero{position:relative;display:grid;grid-template-columns:1.04fr .96fr;gap:64px;align-items:center;width:min(1180px,calc(100% - 40px));min-height:665px;margin:0 auto;padding:68px 0 95px}.landing-hero:before{content:"";position:absolute;width:430px;height:430px;left:-260px;top:30px;border-radius:50%;background:#18d4ff15;filter:blur(2px)}.landing-copy{position:relative;z-index:1}.landing-kicker{display:inline-flex;align-items:center;gap:8px;color:#1676bd;font-size:10px;font-weight:900;letter-spacing:.18em;text-transform:uppercase}.landing-kicker i{width:7px;height:7px;border-radius:50%;background:#18d4ff;box-shadow:0 0 0 5px #18d4ff19}.landing-copy h1{max-width:680px;margin:17px 0 21px;font-size:clamp(42px,5.4vw,71px);line-height:.98;letter-spacing:-.047em}.landing-copy h1 em{display:block;color:#1769ff;font-style:normal}.landing-copy>p{max-width:630px;margin:0;color:#5f7388;font-size:16px;line-height:1.7}.hero-actions{display:flex;gap:12px;margin-top:30px}.cta-primary,.cta-secondary{display:inline-flex;align-items:center;justify-content:center;gap:22px;min-height:49px;padding:0 19px;border-radius:11px;font-size:12px;font-weight:850}.cta-primary{color:#fff!important;background:#1769ff;box-shadow:0 14px 30px #1769ff32}.cta-primary span{font-size:19px}.cta-secondary{border:1px solid #c8d7e5;background:#fff}.cta-secondary.light{border-color:#ffffff3c;background:#ffffff10;color:#fff}.proof-row{display:flex;flex-wrap:wrap;gap:16px;margin-top:27px;color:#5d7083;font-size:10px;font-weight:750}.proof-row span:before{content:"✓";display:inline-grid;place-items:center;width:17px;height:17px;margin-right:6px;border-radius:50%;background:#dff8ef;color:#138063}.product-stage{position:relative;perspective:1000px}.stage-glow{position:absolute;inset:7% -5% -4%;background:radial-gradient(circle,#1769ff36,transparent 66%);filter:blur(20px)}.product-window{position:relative;overflow:hidden;border:1px solid #4c7798;border-radius:18px;background:#071728;color:#fff;box-shadow:0 38px 80px #07152645;transform:rotateY(-5deg) rotateX(2deg)}.product-window:before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 85% 0,#1f568055,transparent 37%);pointer-events:none}.product-window>header,.product-window>footer{position:relative;display:flex;align-items:center;justify-content:space-between;padding:15px 18px;border-bottom:1px solid #ffffff14;font-size:9px;letter-spacing:.08em;color:#a9bfd0}.product-window>header div,.product-window>footer span{display:flex;align-items:center;gap:7px}.product-window>header i,.product-window>footer i{width:7px;height:7px;border-radius:50%;background:#1fd19b;box-shadow:0 0 10px #1fd19b}.product-window>header span{padding:5px 8px;border-radius:20px;background:#ffffff0d}.product-window>header span.online{color:#75e9c4}.product-window>footer{border-top:1px solid #ffffff14;border-bottom:0}.preview-metrics{position:relative;display:grid;grid-template-columns:repeat(3,1fr);gap:1px;margin:16px;background:#ffffff10}.preview-metrics>div{padding:14px;background:#0c2237}.preview-metrics small,.preview-body span{display:block;color:#7f9bb2;font-size:7px;letter-spacing:.15em}.preview-metrics strong{display:block;margin-top:6px;font-size:18px}.preview-body{position:relative;display:grid;grid-template-columns:1.25fr .75fr;gap:16px;padding:0 16px 18px}.preview-body>div,.preview-body aside{padding:13px;border:1px solid #ffffff12;border-radius:12px;background:#0a1d30}.preview-grid{display:grid;grid-template-columns:repeat(8,1fr);gap:3px;margin-top:11px}.preview-grid i{display:block;aspect-ratio:1;border-radius:2px;animation:gridRise .55s ease both;animation-delay:var(--delay)}@keyframes gridRise{from{transform:scale(.25);opacity:0}}.wire-box{position:relative;width:94px;height:94px;margin:19px auto 14px;border:1px solid #58c7eb5c;transform:rotate(30deg) skewY(-10deg)}.wire-box:before,.wire-box:after,.wire-box i{content:"";position:absolute;border:1px solid #58c7eb4f}.wire-box:before{inset:12px}.wire-box:after{inset:26px;background:#18d4ff18}.wire-box i:nth-child(1){width:54px;height:1px;left:19px;top:45px}.wire-box i:nth-child(2){width:1px;height:54px;left:46px;top:19px}.wire-box i:nth-child(3){inset:35px;background:#ffb54788;box-shadow:0 0 18px #ffb547}.preview-body aside p{margin:0;color:#8ba3b7;font-size:8px;line-height:1.5;text-align:center}.landing-section{width:min(1180px,calc(100% - 40px));margin:0 auto;padding:95px 0}.section-intro{max-width:770px}.section-intro.centered{margin:0 auto;text-align:center}.section-intro h2,.architecture-callout h2,.landing-cta h2{margin:12px 0;font-size:clamp(30px,4vw,49px);line-height:1.08;letter-spacing:-.035em}.section-intro>p,.architecture-callout p{color:#6d8093;line-height:1.65}.problem-section{border-top:1px solid #d8e2eb}.problem-grid{display:grid;grid-template-columns:1fr 1fr 1.3fr;gap:17px;margin-top:38px}.problem-grid article,.capability-grid article{padding:28px;border:1px solid #dbe5ed;border-radius:17px;background:#fff;box-shadow:0 12px 30px #0b29420a}.problem-grid article>span,.capability-number{font-size:10px;font-weight:900;letter-spacing:.15em;color:#1681c7}.problem-grid h3,.capability-grid h3,.flow-grid h3{margin:28px 0 9px;font-size:18px}.problem-grid p,.capability-grid p,.flow-grid p{margin:0;color:#6b7e91;font-size:13px;line-height:1.6}.problem-grid .solution-card{color:#fff;background:linear-gradient(140deg,#0b2542,#0e4268);border-color:#1b547b}.solution-card>span{color:#55ddff!important}.solution-card p{color:#bdd0df}.flow-section{width:100%;padding:95px max(20px,calc((100% - 1180px)/2));background:#071526;color:#fff}.flow-section .landing-kicker{color:#3edcff}.flow-grid{position:relative;display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:43px}.flow-grid:before{content:"";position:absolute;left:12%;right:12%;top:25px;border-top:1px dashed #35aede55}.flow-grid article{position:relative;padding:0 18px;text-align:center}.flow-grid article>b{position:relative;z-index:1;display:grid;place-items:center;width:51px;height:51px;margin:0 auto 26px;border:1px solid #35aede8a;border-radius:50%;background:#0a2036;color:#3edcff}.flow-grid p{color:#94aabd}.flow-icon{position:relative;width:64px;height:43px;margin:0 auto;border:1px solid #3fd8ff40;border-radius:10px;background:#0d2942}.flow-icon:after{content:"";position:absolute;inset:10px;border:1px solid #35d6ff;border-radius:5px}.calc-icon:after{border:0;background:linear-gradient(90deg,transparent 35%,#35d6ff 36% 40%,transparent 41% 60%,#35d6ff 61% 65%,transparent 66%),linear-gradient(#35d6ff 0 0) center/70% 2px no-repeat}.twin-icon:after{transform:rotate(35deg);border-color:#ffb547}.alert-icon:after{border:0;background:#ef5b67;clip-path:polygon(50% 0,100% 100%,0 100%)}.capabilities-section{display:grid;grid-template-columns:.8fr 1.2fr;gap:70px;align-items:start}.capability-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.capability-grid .capability-feature{grid-row:span 2;background:linear-gradient(155deg,#f0fbff,#fff)}.capability-grid h3{margin-top:34px}.mini-surface{display:flex;align-items:flex-end;justify-content:center;gap:6px;height:100px;margin-top:23px;padding:15px;border-radius:10px;background:#071526;transform:skewY(-5deg)}.mini-surface i{width:14%;height:var(--h,45%);border-radius:3px 3px 0 0;background:linear-gradient(#18d4ff,#1769ff)}.mini-surface i:nth-child(2){--h:72%}.mini-surface i:nth-child(3){--h:92%;background:linear-gradient(#ffb547,#18d4ff)}.mini-surface i:nth-child(4){--h:67%}.mini-surface i:nth-child(5){--h:37%}.architecture-callout{display:grid;grid-template-columns:1fr 1fr;gap:50px;align-items:center;padding:55px;border-radius:24px;background:#e8f4fb}.architecture-flow{display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap}.architecture-flow span{padding:16px;border:1px solid #bad7e8;border-radius:11px;background:#fff;font-size:11px;font-weight:850}.architecture-flow i{color:#1681c7;font-style:normal;font-size:18px}.landing-cta{width:min(1180px,calc(100% - 40px));margin:95px auto;padding:74px 30px;border-radius:26px;text-align:center;color:#fff;background:radial-gradient(circle at 78% 10%,#1769ff88,transparent 35%),linear-gradient(135deg,#071526,#0c3557);box-shadow:0 30px 65px #0715262b}.landing-cta>span{font-size:10px;letter-spacing:.2em;color:#4adeff}.landing-cta p{color:#afc3d3}.landing-cta .hero-actions{justify-content:center}.landing-footer{display:flex;align-items:center;justify-content:space-between;width:min(1180px,calc(100% - 40px));margin:0 auto;padding:28px 0;border-top:1px solid #dbe4ec;color:#6b7e91;font-size:11px}.reveal{opacity:0;transform:translateY(18px);transition:opacity .65s ease,transform .65s ease}.reveal.visible{opacity:1;transform:none}
.admin-kpis{margin-bottom:18px}.admin-actions{display:flex;gap:9px;align-items:center}.admin-actions .compact{width:auto}.quick-prompts{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0}.quick-prompt{width:auto;margin:0;padding:7px 9px;border:1px solid #c8d9e7;background:#fff;color:#28536f;font-size:10px}.report-link{display:inline-flex;align-items:center;justify-content:center;padding:10px 14px;border-radius:9px;background:#1769ff;color:#fff!important;font-size:11px;font-weight:850;text-decoration:none}.assistant-meta{display:flex;align-items:center;justify-content:space-between;gap:10px;color:#6f8095;font-size:10px}
@media(max-width:980px){.landing-menu{gap:12px}.landing-hero{grid-template-columns:1fr;gap:45px;padding-top:45px}.product-stage{width:min(620px,100%);margin:0 auto}.problem-grid{grid-template-columns:1fr 1fr}.problem-grid .solution-card{grid-column:1/-1}.capabilities-section{grid-template-columns:1fr}.architecture-callout{grid-template-columns:1fr}.landing-copy h1 em{display:inline}}
@media(max-width:760px){.menu-toggle{display:block}.landing-menu{position:absolute;display:none;top:68px;left:0;right:0;align-items:stretch;flex-direction:column;gap:5px;padding:15px;border:1px solid #d9e4ec;border-radius:14px;background:#fff;box-shadow:0 20px 40px #0715261f}.landing-menu.open{display:flex}.landing-menu>a{padding:11px}.landing-hero{min-height:0}.product-window{transform:none}.preview-body{grid-template-columns:1fr}.problem-grid,.capability-grid,.flow-grid{grid-template-columns:1fr}.capability-grid .capability-feature{grid-row:auto}.flow-grid:before{display:none}.flow-grid article{padding:18px;border:1px solid #ffffff13;border-radius:14px}.flow-grid article>b{margin-bottom:15px}.architecture-callout{padding:32px 22px}.architecture-flow{justify-content:flex-start}.landing-footer{align-items:flex-start;flex-direction:column;gap:16px}.landing-footer p{margin:0}.admin-actions{width:100%;flex-wrap:wrap}.admin-actions>*{flex:1}}
@media(max-width:480px){.landing-nav,.landing-hero,.landing-section,.landing-cta,.landing-footer{width:min(100% - 26px,1180px)}.landing-copy h1{font-size:42px}.hero-actions{align-items:stretch;flex-direction:column}.proof-row{align-items:flex-start;flex-direction:column;gap:10px}.preview-metrics{grid-template-columns:1fr;margin:11px}.preview-metrics>div{display:flex;align-items:center;justify-content:space-between;padding:10px}.preview-body{padding:0 11px 11px}.landing-section{padding:70px 0}.flow-section{width:100%;padding:70px 13px}.landing-cta{margin-top:70px;margin-bottom:70px}.architecture-callout{width:calc(100% - 26px)}}

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\templates\admin.html`

```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#071526">
  <title>Painel administrativo | BoxTwin</title>
  <link rel="manifest" href="/manifest.webmanifest">
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="/"><div class="brand-mark">H</div><div><span>HYDROGENI · OPERAÇÃO REAL</span><h1>Central BoxTwin</h1><p>{{ box_name }} · {{ node_id }}</p></div></a>
    <div class="status-group"><a class="badge" href="/">PROJETO</a><a class="badge" href="/simulador">SIMULADOR</a><form method="post" action="/logout"><button class="badge" type="submit">SAIR</button></form></div>
  </header>
  <main>
    <section class="hero">
      <div><span class="eyebrow">PAINEL ADMINISTRATIVO</span><h2>Operação, incidentes e decisão assistida</h2><p>Acompanhe indicadores reais do BoxNode, trate anomalias com rastreabilidade e gere um relatório consolidado em PDF.</p></div>
      <div class="box-spec"><span>Estado do BoxNode</span><strong id="adminConnection">Conectando...</strong><small>Atualização por eventos em tempo real</small></div>
    </section>

    <section class="metrics admin-kpis">
      <article><small>Ocupação atual</small><div><strong id="adminOccupancy">-</strong><span>%</span></div><em id="adminVolume">Sem leitura</em></article>
      <article><small>Confiança média</small><div><strong id="adminConfidence">-</strong><span>%</span></div><em>Últimas 100 leituras</em></article>
      <article><small>Incidentes ativos</small><div><strong id="adminActive">-</strong></div><em>Abertos, cientes ou em atendimento</em></article>
      <article><small>Incidentes resolvidos</small><div><strong id="adminResolved">-</strong></div><em>Histórico operacional</em></article>
      <article><small>Modo do sensor</small><div><strong id="adminSensorMode">-</strong></div><em id="adminReadingTime">Aguardando telemetria</em></article>
    </section>

    <section class="admin-grid">
      <article class="panel">
        <div class="panel-heading"><div><span class="eyebrow">FILA OPERACIONAL</span><h3>Anomalias recentes</h3></div><div class="admin-actions"><a class="report-link" href="/admin/reports/operational.pdf">Baixar relatório PDF</a><button id="refreshAdmin" class="secondary compact">Atualizar</button></div></div>
        <div id="anomalyList" class="incident-list"></div>
      </article>
      <aside class="panel assistant-panel">
        <span class="eyebrow">ASSISTENTE TÉCNICO · RAG</span><h3>Copiloto de tratativas</h3><p>O assistente recebe o contexto da última leitura e cita os procedimentos internos usados como fonte.</p>
        <div class="quick-prompts"><button class="quick-prompt" data-prompt="Analise o estado atual do box e indique os próximos passos seguros.">Analisar estado atual</button><button class="quick-prompt" data-prompt="Como tratar uma obstrução do sensor com segurança?">Tratar obstrução</button><button class="quick-prompt" data-prompt="Como validar uma leitura com baixa confiança?">Baixa confiança</button></div>
        <div id="assistantAnswer" class="assistant-answer">Selecione uma anomalia ou faça uma pergunta operacional.</div>
        <form id="assistantForm"><textarea id="assistantQuestion" rows="4" maxlength="1200" placeholder="Ex.: O que devo verificar antes de recalibrar o box?" required></textarea><div class="assistant-meta"><span>Respostas de apoio - decisão final humana</span><span id="assistantCount">0/1200</span></div><button class="primary" type="submit">Consultar assistente</button></form>
      </aside>
    </section>

    <section class="admin-grid management-grid">
      <article class="panel"><span class="eyebrow">RESPONSÁVEIS</span><h3>Destinatários e equipes</h3><form id="recipientForm" class="inline-form"><input id="recipientName" placeholder="Nome do responsável" required><select id="recipientType"><option value="administrator">Administrador</option><option value="team">Equipe</option></select><input id="recipientTeam" placeholder="Equipe/setor"><input id="recipientEmail" type="email" placeholder="E-mail"><input id="recipientPhone" placeholder="WhatsApp/SMS: +5598..."><button class="primary">Cadastrar</button></form><div id="recipientList" class="compact-list"></div></article>
      <article class="panel"><span class="eyebrow">AUTOMAÇÃO</span><h3>Regras e escalonamento</h3><form id="ruleForm" class="inline-form"><select id="ruleType"><option value="*">Todas as anomalias</option><option value="capacity">Capacidade</option><option value="confidence">Baixa confiança</option><option value="obstruction">Obstrução</option></select><select id="ruleSeverity"><option value="*">Toda severidade</option><option value="warning">Atenção</option><option value="danger">Crítica</option></select><select id="ruleRecipient" required></select><select id="ruleChannel"><option value="email">E-mail</option><option value="twilio">Twilio</option></select><input id="ruleDelay" type="number" min="0" value="0" placeholder="Minutos"><button class="primary">Criar regra</button></form><div id="ruleList" class="compact-list"></div></article>
    </section>
    <section class="panel"><div class="panel-heading"><div><span class="eyebrow">CANAIS EXTERNOS</span><h3>Histórico de notificações</h3></div></div><div id="notificationList" class="notification-list"></div></section>
    <footer><span>HydrogenI · BoxTwin 3D</span><p>Painel administrativo e operacional do BoxNode.</p></footer>
  </main>
  <script src="{{ url_for('static', filename='admin.js') }}"></script>
</body>
</html>

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\templates\anomaly.html`

```html
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#071526"><title>Incidente #{{ anomaly_id }} | BoxTwin</title><link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head><body>
<header class="topbar"><div class="brand"><div class="brand-mark">H</div><div><span>HYDROGENI · INCIDENTE</span><h1>Anomalia #{{ anomaly_id }}</h1></div></div><a class="badge" href="/admin">← Central operacional</a></header><main>
<section id="incidentSummary" class="hero"><div><span class="eyebrow">CARREGANDO</span><h2>Detalhes da ocorrência</h2></div></section>
<section class="admin-grid"><article class="panel"><span class="eyebrow">DADOS DA LEITURA</span><h3>Evidências</h3><div id="readingDetail" class="detail-grid"></div><div id="incidentGrid" class="grid"></div></article><aside class="panel"><span class="eyebrow">TRATATIVA</span><h3>Atualizar situação</h3><form id="statusForm" class="stack-form"><select id="incidentStatus"><option value="acknowledged">Ciente</option><option value="in_progress">Em atendimento</option><option value="resolved">Resolvida</option><option value="false_positive">Falso positivo</option></select><textarea id="incidentNote" rows="4" placeholder="Observação técnica"></textarea><button class="primary">Salvar atualização</button></form><button id="suggestTreatment" class="secondary">Sugerir tratativa com IA</button><div id="treatment" class="assistant-answer">Aguardando consulta.</div></aside></section>
<section class="panel"><span class="eyebrow">RASTREABILIDADE</span><h3>Linha do tempo</h3><div id="timeline" class="timeline"></div></section></main><script>window.ANOMALY_ID={{ anomaly_id }};</script><script src="{{ url_for('static', filename='anomaly.js') }}"></script></body></html>

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\templates\index.html`

```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#061426">
  <meta name="description" content="HydrogenI BoxTwin 3D: medição inteligente de volume, gêmeo digital e gestão de anomalias para boxes de granéis.">
  <title>HydrogenI | BoxTwin 3D</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body class="landing-page">
  <nav class="landing-nav" aria-label="Navegação principal">
    <a class="landing-brand" href="/" aria-label="HydrogenI - início"><span>H</span><div><b>HYDROGENI</b><small>BOXTWIN 3D</small></div></a>
    <button id="menuToggle" class="menu-toggle" aria-label="Abrir menu" aria-expanded="false">Menu</button>
    <div id="landingMenu" class="landing-menu">
      <a href="#solucao">Solução</a><a href="#como-funciona">Como funciona</a><a href="#recursos">Recursos</a>
      <a class="nav-secondary" href="/login">Painel administrativo</a><a class="nav-primary" href="/simulador">Abrir simulador</a>
    </div>
  </nav>

  <main class="landing-main">
    <section class="landing-hero">
      <div class="landing-copy reveal">
        <span class="landing-kicker"><i></i> Gêmeo digital para granéis</span>
        <h1>Transforme uma pilha irregular em uma <em>medição confiável.</em></h1>
        <p>O BoxTwin 3D converte dados de profundidade em volume, ocupação e alertas operacionais - com histórico rastreável, assistente técnico e funcionamento local.</p>
        <div class="hero-actions"><a class="cta-primary" href="/simulador">Explorar demonstração <span>→</span></a><a class="cta-secondary" href="/login">Acessar operação</a></div>
        <div class="proof-row"><span>64 zonas de leitura</span><span>Operação offline</span><span>Alertas em tempo real</span></div>
      </div>
      <div class="product-stage reveal" aria-label="Prévia do painel BoxTwin">
        <div class="stage-glow"></div>
        <article class="product-window">
          <header><div><i></i><b>{{ node_id }}</b></div><span id="landingStatus">Conectando</span></header>
          <div class="preview-metrics"><div><small>Ocupação</small><strong id="landingOccupancy">--%</strong></div><div><small>Confiança</small><strong id="landingConfidence">--%</strong></div><div><small>Volume</small><strong id="landingVolume">-- m³</strong></div></div>
          <div class="preview-body"><div><span>SUPERFÍCIE 8 x 8</span><div id="landingGrid" class="preview-grid"></div></div><aside><span>BOX DIGITAL</span><div class="wire-box"><i></i><i></i><i></i></div><p id="landingReadingState">Aguardando leitura do BoxNode.</p></aside></div>
          <footer><span><i></i> Telemetria ativa</span><small>{{ box_name }}</small></footer>
        </article>
      </div>
    </section>

    <section id="solucao" class="landing-section problem-section reveal">
      <div class="section-intro"><span class="landing-kicker">O desafio</span><h2>Medir granéis não deveria depender apenas de estimativa visual.</h2></div>
      <div class="problem-grid">
        <article><span>01</span><h3>Superfície irregular</h3><p>Pilhas, inclinações e vazios tornam a avaliação manual imprecisa.</p></article>
        <article><span>02</span><h3>Baixa rastreabilidade</h3><p>Sem histórico estruturado, variações e incidentes ficam difíceis de comprovar.</p></article>
        <article class="solution-card"><span>SOLUÇÃO</span><h3>Um box que entende seu próprio volume.</h3><p>A matriz de profundidade alimenta um gêmeo digital e transforma 64 pontos em informação operacional.</p></article>
      </div>
    </section>

    <section id="como-funciona" class="landing-section flow-section reveal">
      <div class="section-intro centered"><span class="landing-kicker">Fluxo de dados</span><h2>Da leitura à decisão, em quatro etapas.</h2></div>
      <div class="flow-grid">
        <article><b>1</b><div class="flow-icon sensor-icon"></div><h3>Captura</h3><p>O sensor registra uma matriz de profundidade com 64 zonas.</p></article>
        <article><b>2</b><div class="flow-icon calc-icon"></div><h3>Cálculo</h3><p>A calibração vazia é comparada à superfície atual do material.</p></article>
        <article><b>3</b><div class="flow-icon twin-icon"></div><h3>Gêmeo digital</h3><p>Volume, ocupação, alturas e confiança são atualizados no painel.</p></article>
        <article><b>4</b><div class="flow-icon alert-icon"></div><h3>Ação</h3><p>Anomalias geram tratativas, notificações e registro operacional.</p></article>
      </div>
    </section>

    <section id="recursos" class="landing-section capabilities-section reveal">
      <div class="section-intro"><span class="landing-kicker">Plataforma operacional</span><h2>Um MVP organizado para demonstrar hoje e evoluir amanhã.</h2><p>A arquitetura separa experiência pública, ambiente simulado e gestão administrativa.</p></div>
      <div class="capability-grid">
        <article class="capability-feature"><span class="capability-number">01</span><h3>Visualização 3D</h3><p>Mapa de altura e superfície tridimensional gerados diretamente no navegador.</p><div class="mini-surface"><i></i><i></i><i></i><i></i><i></i></div></article>
        <article><span class="capability-number">02</span><h3>Assistente técnico</h3><p>Consulta procedimentos internos por RAG local, com possibilidade de Grok e fontes rastreáveis.</p></article>
        <article><span class="capability-number">03</span><h3>Relatório PDF</h3><p>Consolida indicadores, leituras e incidentes em um documento pronto para apresentação.</p></article>
        <article><span class="capability-number">04</span><h3>Gestão de incidentes</h3><p>Fila, ciência, atendimento, resolução, evidências e linha do tempo.</p></article>
        <article><span class="capability-number">05</span><h3>Integrações</h3><p>Notificações opcionais por e-mail e Twilio sem interromper o ciclo de medição.</p></article>
      </div>
    </section>

    <section class="landing-section architecture-callout reveal">
      <div><span class="landing-kicker">Arquitetura evolutiva</span><h2>O simulador usa o mesmo contrato de dados do sensor.</h2><p>Trocar o modo virtual pelo hardware não exige reconstruir cálculo, banco de dados, APIs ou painel.</p></div>
      <div class="architecture-flow"><span>Sensor 8 x 8</span><i>→</i><span>Motor volumétrico</span><i>→</i><span>BoxTwin + alertas</span></div>
    </section>

    <section class="landing-cta reveal"><span>HYDROGENI · BOXTWIN 3D</span><h2>Veja o gêmeo digital em funcionamento.</h2><p>Explore cenários conhecidos, gere leituras e acompanhe o fluxo completo do MVP.</p><div class="hero-actions"><a class="cta-primary" href="/simulador">Iniciar simulação <span>→</span></a><a class="cta-secondary light" href="/login">Entrar no painel</a></div></section>
  </main>

  <footer class="landing-footer"><a class="landing-brand" href="/"><span>H</span><div><b>HYDROGENI</b><small>BOXTWIN 3D</small></div></a><p>Medição automatizada de volume e gestão inteligente de boxes.</p><small>Projeto HydrogenI · 2026</small></footer>
  <script src="{{ url_for('static', filename='landing.js') }}"></script>
</body>
</html>

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\templates\login.html`

```html
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#071526"><title>Acesso administrativo | BoxTwin</title><link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body class="auth-page"><main class="auth-card"><div class="brand"><div class="brand-mark">H</div><div><span>HYDROGENI</span><h1>BoxTwin Admin</h1></div></div><p>Acesso restrito aos administradores da operação.</p>{% if error %}<div class="alert danger">{{ error }}</div>{% endif %}<form method="post"><label>Usuário<input name="username" autocomplete="username" required></label><label>Senha<input name="password" type="password" autocomplete="current-password" required></label><button class="primary" type="submit">Entrar</button></form><a href="/">Voltar à página do projeto</a></main></body></html>

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\boxtwin\templates\simulator.html`

```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#071526">
  <link rel="manifest" href="/manifest.webmanifest">
  <title>Simulador | HydrogenI BoxTwin 3D</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="/"><div class="brand-mark">H</div><div><span>HYDROGENI · BOXNODE</span><h1>BoxTwin 3D</h1><p>{{ box_name }} · {{ node_id }}</p></div></a>
    <div class="status-group"><a href="/" class="badge">PROJETO</a><a href="/admin" class="badge">ÁREA ADMIN</a><b id="modeBadge" class="badge demo">MODO DEMONSTRAÇÃO</b><b id="connection" class="badge">Conectando…</b></div>
  </header>
  <main>
    <section class="hero"><div><span class="eyebrow">AMBIENTE SIMULADO</span><h2>Volume do box em tempo real</h2><p>Protótipo demonstrável com matriz virtual 8 x 8. A mesma interface receberá as leituras do sensor físico quando o hardware estiver disponível.</p></div><div class="box-spec"><span>Capacidade cadastrada</span><strong id="boxCapacity">-</strong><small id="boxDimensions">Carregando dimensões...</small></div></section>
    <section class="metrics">
      <article><small>Volume estimado</small><div><strong id="volume">-</strong><span>m³</span></div><em>Integração das 64 zonas</em></article>
      <article><small>Ocupação</small><div><strong id="capacity">-</strong><span>%</span></div><div class="meter"><i id="capacityBar"></i></div></article>
      <article><small>Altura média</small><div><strong id="avgHeight">-</strong><span>cm</span></div><em id="maxHeight">Pico: -</em></article>
      <article><small>Confiança</small><div><strong id="confidence">-</strong><span>%</span></div><em><span id="zones">-</span> de 64 zonas válidas</em></article>
      <article><small>Erro da simulação</small><div><strong id="referenceError">-</strong><span>p.p.</span></div><em id="referenceValue">Referência: -</em></article>
    </section>
    <section id="demoPanel" class="demo-panel panel"><div class="panel-heading"><div><span class="eyebrow">CONTROLE DO MVP</span><h3>Cenários de demonstração</h3></div><button id="setup" class="primary compact">Preparar demonstração</button></div><p>Selecione um cenário para simular a superfície do fertilizante e gerar uma nova medição imediatamente.</p><div id="scenarios" class="scenario-list"></div></section>
    <section class="workspace">
      <article class="panel twin-panel"><div class="panel-heading"><div><span class="eyebrow">VISTA TRIDIMENSIONAL</span><h3>Gêmeo digital do box</h3></div><span id="updated" class="muted">Sem leitura</span></div><canvas id="twinCanvas" aria-label="Representação tridimensional da carga"></canvas><div class="legend"><span>Baixo</span><i></i><span>Alto</span></div></article>
      <article class="panel map-panel"><div class="panel-heading"><div><span class="eyebrow">MAPA DE ALTURA</span><h3>Superfície 8 x 8</h3></div><span class="unit">cm</span></div><div id="grid" class="grid"></div></article>
      <aside class="panel control-panel"><div><span class="eyebrow">DIAGNÓSTICO</span><h3>Estado operacional</h3></div><div id="alerts" class="alerts"><p>Nenhum dado disponível.</p></div><button id="capture" class="primary">Capturar novamente</button><button id="calibrate" class="secondary">Calibrar box vazio</button></aside>
    </section>
    <section class="panel history-panel"><div class="panel-heading"><div><span class="eyebrow">HISTÓRICO LOCAL</span><h3>Evolução da ocupação</h3></div><span class="muted">Últimas 20 leituras</span></div><canvas id="historyCanvas" aria-label="Histórico de ocupação"></canvas></section>
    <footer><span>HydrogenI · BoxTwin 3D</span><p>Ambiente simulado do MVP para medição automatizada de volume.</p></footer>
  </main>
  <script src="{{ url_for('static', filename='app.js') }}"></script>
</body>
</html>

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\tests\test_admin.py`

```python
from boxtwin import create_app


def make_client(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "admin.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
        "SECRET_KEY": "test-secret",
        "ADMIN_USERNAME": "admin",
        "ADMIN_PASSWORD": "test-pass",
        "EMAIL_ENABLED": False,
        "TWILIO_ENABLED": False,
        "TWILIO_VALIDATE_SIGNATURE": False,
    })
    return app.test_client()


def login(client):
    return client.post("/login", data={"username": "admin", "password": "test-pass"})


def test_admin_requires_login(tmp_path):
    response = make_client(tmp_path).get("/admin")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_login_and_rag(tmp_path):
    client = make_client(tmp_path)
    assert login(client).status_code == 302
    response = client.post("/api/admin/assistant", json={"question": "Como tratar obstrução do sensor?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["mode"] == "local-rag"
    assert data["sources"]


def test_public_landing_and_simulator_are_separate(tmp_path):
    client = make_client(tmp_path)
    landing = client.get("/")
    simulator = client.get("/simulador")
    assert landing.status_code == 200
    assert b"Transforme uma pilha irregular" in landing.data
    assert simulator.status_code == 200
    assert b"AMBIENTE SIMULADO" in simulator.data


def test_admin_summary_and_pdf_report(tmp_path):
    client = make_client(tmp_path)
    login(client)
    client.post("/api/demo/setup")
    client.post("/api/demo/scenario/flat_50")
    summary = client.get("/api/admin/summary")
    assert summary.status_code == 200
    assert summary.get_json()["latest"]["capacity_percent"] > 0
    report = client.get("/admin/reports/operational.pdf")
    assert report.status_code == 200
    assert report.mimetype == "application/pdf"
    assert report.data.startswith(b"%PDF")
    assert len(report.data) > 3000


def test_anomaly_workflow(tmp_path):
    client = make_client(tmp_path)
    login(client)
    client.post("/api/demo/setup")
    client.post("/api/demo/scenario/obstruction")
    anomalies = client.get("/api/admin/anomalies").get_json()
    assert anomalies
    open_item = next(item for item in anomalies if item["status"] == "open")
    response = client.post(f"/api/admin/anomalies/{open_item['id']}/acknowledge", json={"note": "Teste"})
    assert response.status_code == 200


def test_recipient_rule_detail_and_twilio_reply(tmp_path):
    client = make_client(tmp_path)
    login(client)
    recipient = client.post("/api/admin/recipients", json={"name": "Equipe de manutenção", "recipient_type": "team", "phone": "whatsapp:+5598999999999"})
    assert recipient.status_code == 201
    rule = client.post("/api/admin/rules", json={"anomaly_type": "obstruction", "recipient_id": recipient.get_json()["id"], "channel": "twilio", "escalation_minutes": 10})
    assert rule.status_code == 201
    client.post("/api/demo/setup")
    reading = client.post("/api/demo/scenario/obstruction").get_json()
    anomaly_id = reading["anomaly_ids"][0]
    assert client.get(f"/api/admin/anomalies/{anomaly_id}").status_code == 200
    reply = client.post("/api/webhooks/twilio/incoming", data={"Body": f"2 {anomaly_id}", "From": "whatsapp:+5598999999999"})
    assert reply.status_code == 200
    detail = client.get(f"/api/admin/anomalies/{anomaly_id}").get_json()
    assert detail["anomaly"]["status"] == "in_progress"

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\tests\test_api.py`

```python
import pytest

from boxtwin import create_app


def test_health(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "online"


def test_demo_setup_and_scenario(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    client = app.test_client()

    setup = client.post("/api/demo/setup")
    assert setup.status_code == 201
    assert setup.get_json()["reading"]["scenario"] == "pile"

    reading = client.post("/api/demo/scenario/flat_50")
    assert reading.status_code == 201
    payload = reading.get_json()
    assert payload["capacity_percent"] == pytest.approx(50, abs=0.2)
    assert payload["reference_error_points"] <= 0.2

    latest = client.get("/api/readings/latest").get_json()
    assert latest["scenario"] == "flat_50"

    obstruction = client.post("/api/demo/scenario/obstruction").get_json()
    assert obstruction["confidence_percent"] < 70
    assert any(alert["type"] == "obstruction" for alert in obstruction["alerts"])


def test_invalid_demo_scenario(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    response = app.test_client().post("/api/demo/scenario/inexistente")
    assert response.status_code == 404

```

### 📄 `HydrogenI_BoxTwin_Railway_Ready_v6\tests\test_volume.py`

```python
import pytest

from boxtwin.services import AlertService, VolumeService


def grid(value):
    return [[value for _ in range(8)] for _ in range(8)]


def test_half_full_box_volume():
    service = VolumeService(length_m=0.60, width_m=0.40, height_m=0.50)
    result = service.calculate(grid(500), grid(250))
    assert result["volume_m3"] == pytest.approx(0.06)
    assert result["capacity_percent"] == pytest.approx(50.0)
    assert result["confidence_percent"] == 100.0


def test_capacity_alert():
    alerts = AlertService(85, 70).evaluate({"capacity_percent": 90, "confidence_percent": 100, "valid_zones": 64})
    assert alerts[0]["type"] == "capacity"


def test_invalid_grid_shape():
    service = VolumeService(length_m=0.60, width_m=0.40, height_m=0.50)
    with pytest.raises(ValueError):
        service.calculate([[500]], [[250]])

```

### 📄 `tests\test_admin.py`

```python
from boxtwin import create_app


def make_client(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "admin.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
        "SECRET_KEY": "test-secret",
        "ADMIN_USERNAME": "admin",
        "ADMIN_PASSWORD": "test-pass",
        "EMAIL_ENABLED": False,
        "TWILIO_ENABLED": False,
        "TWILIO_VALIDATE_SIGNATURE": False,
    })
    return app.test_client()


def login(client):
    return client.post("/login", data={"username": "admin", "password": "test-pass"})


def test_admin_requires_login(tmp_path):
    response = make_client(tmp_path).get("/admin")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_login_and_rag(tmp_path):
    client = make_client(tmp_path)
    assert login(client).status_code == 302
    response = client.post("/api/admin/assistant", json={"question": "Como tratar obstrução do sensor?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["mode"] == "local-rag"
    assert data["sources"]


def test_anomaly_workflow(tmp_path):
    client = make_client(tmp_path)
    login(client)
    client.post("/api/demo/setup")
    client.post("/api/demo/scenario/obstruction")
    anomalies = client.get("/api/admin/anomalies").get_json()
    assert anomalies
    open_item = next(item for item in anomalies if item["status"] == "open")
    response = client.post(f"/api/admin/anomalies/{open_item['id']}/acknowledge", json={"note": "Teste"})
    assert response.status_code == 200


def test_recipient_rule_detail_and_twilio_reply(tmp_path):
    client = make_client(tmp_path)
    login(client)
    recipient = client.post("/api/admin/recipients", json={"name": "Equipe de manutenção", "recipient_type": "team", "phone": "whatsapp:+5598999999999"})
    assert recipient.status_code == 201
    rule = client.post("/api/admin/rules", json={"anomaly_type": "obstruction", "recipient_id": recipient.get_json()["id"], "channel": "twilio", "escalation_minutes": 10})
    assert rule.status_code == 201
    client.post("/api/demo/setup")
    reading = client.post("/api/demo/scenario/obstruction").get_json()
    anomaly_id = reading["anomaly_ids"][0]
    assert client.get(f"/api/admin/anomalies/{anomaly_id}").status_code == 200
    reply = client.post("/api/webhooks/twilio/incoming", data={"Body": f"2 {anomaly_id}", "From": "whatsapp:+5598999999999"})
    assert reply.status_code == 200
    detail = client.get(f"/api/admin/anomalies/{anomaly_id}").get_json()
    assert detail["anomaly"]["status"] == "in_progress"

```

### 📄 `tests\test_api.py`

```python
import pytest

from boxtwin import create_app


def test_health(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "online"


def test_demo_setup_and_scenario(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    client = app.test_client()

    setup = client.post("/api/demo/setup")
    assert setup.status_code == 201
    assert setup.get_json()["reading"]["scenario"] == "pile"

    reading = client.post("/api/demo/scenario/flat_50")
    assert reading.status_code == 201
    payload = reading.get_json()
    assert payload["capacity_percent"] == pytest.approx(50, abs=0.2)
    assert payload["reference_error_points"] <= 0.2

    latest = client.get("/api/readings/latest").get_json()
    assert latest["scenario"] == "flat_50"

    obstruction = client.post("/api/demo/scenario/obstruction").get_json()
    assert obstruction["confidence_percent"] < 70
    assert any(alert["type"] == "obstruction" for alert in obstruction["alerts"])


def test_invalid_demo_scenario(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    response = app.test_client().post("/api/demo/scenario/inexistente")
    assert response.status_code == 404

```

### 📄 `tests\test_volume.py`

```python
import pytest

from boxtwin.services import AlertService, VolumeService


def grid(value):
    return [[value for _ in range(8)] for _ in range(8)]


def test_half_full_box_volume():
    service = VolumeService(length_m=0.60, width_m=0.40, height_m=0.50)
    result = service.calculate(grid(500), grid(250))
    assert result["volume_m3"] == pytest.approx(0.06)
    assert result["capacity_percent"] == pytest.approx(50.0)
    assert result["confidence_percent"] == 100.0


def test_capacity_alert():
    alerts = AlertService(85, 70).evaluate({"capacity_percent": 90, "confidence_percent": 100, "valid_zones": 64})
    assert alerts[0]["type"] == "capacity"


def test_invalid_grid_shape():
    service = VolumeService(length_m=0.60, width_m=0.40, height_m=0.50)
    with pytest.raises(ValueError):
        service.calculate([[500]], [[250]])

```
