# Deploy no Railway - HydrogenI BoxTwin

Este guia reflete o estado atual do projeto em 20/08/2026.

Hoje o deploy no Railway já está compatível com:

- painel web;
- login administrativo;
- simulador e captura local;
- alertas e tratativas;
- exportação de relatório em PDF e Excel;
- ingestão de leituras vindas do Raspberry;
- sincronização idempotente Raspberry -> Railway por `EDGE_SYNC_TOKEN`.

## 1. Pré-requisitos

- repositório atualizado no GitHub;
- projeto criado no Railway;
- variáveis de ambiente configuradas;
- branch com o código atual contendo:
  - `boxtwin/routes.py` com `/api/edge/readings`, `/admin/reports` e exportação `.xlsx`;
  - `boxtwin/runtime.py` com fila de sincronização;
  - `boxtwin/database.py` com `sync_queue` e `reading_uuid`;
  - `requirements.txt` com `openpyxl`, `reportlab`, `gunicorn` e `tzdata`.

## 2. Build e start já esperados

O arquivo [railway.json](C:/Users/junio/Desktop/PROJETOS%20PYHTON/HydrogenI%20-%20projeto/HydrogenY-BoxTwin/HydrogenI-BoxTwin/railway.json) já está coerente com o deploy atual:

```json
{
  "build": { "builder": "RAILPACK" },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120 app:app",
    "healthcheckPath": "/api/health"
  }
}
```

Você não precisa trocar isso agora, salvo se quiser ajustar concorrência depois.

## 3. Variáveis mínimas recomendadas no Railway

Use estas variáveis como base:

```env
APP_HOST=0.0.0.0
APP_PORT=5000
APP_DEBUG=false

SENSOR_MODE=mock
BOX_NODE_ID=BOX-DEMO-01
BOX_NAME=Box reduzido HydrogenI
BOX_LENGTH_M=0.60
BOX_WIDTH_M=0.40
BOX_HEIGHT_M=0.50
SAMPLE_INTERVAL_SECONDS=5
CAPACITY_ALERT_PERCENT=85
MIN_CONFIDENCE_PERCENT=70

DATABASE_PATH=data/boxtwin.db
CALIBRATION_PATH=data/calibration.json

SECRET_KEY=troque-por-uma-chave-longa-e-aleatoria
ADMIN_USERNAME=admin
ADMIN_PASSWORD=HydrogenI@2026

NOTIFY_COOLDOWN_SECONDS=300
EMAIL_ENABLED=true
ALERT_EMAIL_TO=hydrogeni.boxtwin@gmail.com

TWILIO_ENABLED=false
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM=
TWILIO_TO=
TWILIO_VALIDATE_SIGNATURE=true

PUBLIC_BASE_URL=https://hydrogeni-boxtwin-production.up.railway.app

RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=onboarding@resend.dev

GROQ_ENABLED=true
GROQ_API_KEY=gsk_...
GROQ_MODEL=openai/gpt-oss-120b

EDGE_SYNC_TOKEN=um-token-longo-e-unico
```

## 4. Variáveis opcionais mas recomendadas

Estas ajudam a preparar o ambiente central para sincronização e retenção:

```env
EDGE_SYNC_ENABLED=false
EDGE_SYNC_TARGET_URL=
EDGE_SYNC_TIMEOUT_SECONDS=15
EDGE_SYNC_BATCH_SIZE=20

AUTO_CLEANUP_ENABLED=true
READINGS_RETENTION_DAYS=45
NOTIFICATIONS_RETENTION_DAYS=60
INCIDENTS_RETENTION_DAYS=180
SYNC_QUEUE_RETENTION_DAYS=7
```

Notas:

- no Railway, `EDGE_SYNC_ENABLED` pode ficar `false`, porque ele é o destino central;
- no Raspberry, `EDGE_SYNC_ENABLED` deve ficar `true`;
- `EDGE_SYNC_TOKEN` precisa ser exatamente o mesmo nos dois lados;
- `PUBLIC_BASE_URL` deve ficar sem barra final para evitar inconsistência em links e webhooks.

## 5. Como subir para o Railway

Depois de enviar a branch correta para o GitHub:

```bash
git push origin dev/d-junior
```

No Railway:

1. abra o projeto;
2. conecte o repositório GitHub;
3. selecione a branch desejada;
4. confirme as variáveis de ambiente;
5. dispare o deploy.

## 6. O que validar após o deploy

Valide estes endpoints e telas:

- `/api/health`
- `/simulador`
- `/admin`
- `/admin/reports`
- exportação PDF em `/admin/reports/operational.pdf`
- exportação Excel em `/admin/reports/operational.xlsx`

Se o Raspberry já estiver apontando para o Railway, valide também:

- `POST /api/edge/readings`
- `GET /api/admin/sync-status`

## 7. Cenário correto Raspberry -> Railway

O fluxo esperado é:

1. Raspberry captura a leitura;
2. salva primeiro no SQLite local;
3. adiciona item à `sync_queue`;
4. tenta enviar ao Railway;
5. se a internet falhar, mantém pendente;
6. quando a internet voltar, reenvia;
7. o Railway aceita sem duplicar usando `reading_uuid`.

Isso já está implementado no código atual.

## 8. Cuidados importantes antes de produção

- rotacionar `RESEND_API_KEY` e `GROQ_API_KEY` se elas já foram expostas em conversa, print ou commit;
- trocar `SECRET_KEY` por um valor forte e exclusivo;
- trocar `ADMIN_PASSWORD` por senha real de operação;
- confirmar se `EMAIL_ENABLED=true` só quando `RESEND_API_KEY` estiver válida;
- revisar o arquivo [.env.example](C:/Users/junio/Desktop/PROJETOS%20PYHTON/HydrogenI%20-%20projeto/HydrogenY-BoxTwin/HydrogenI-BoxTwin/.env.example) para usar como referência limpa;
- não subir `data/offline_queue.json` preenchido para produção.

## 9. Estado atual do projeto para deploy

Hoje o projeto está pronto para deploy de demonstração e homologação no Railway.

Ele já entrega boa impressão para apresentação porque reúne:

- painel administrativo;
- simulador com anomalias;
- tratativa operacional;
- assistente com base contextual;
- relatórios exportáveis;
- preparação para operação híbrida Raspberry + nuvem.

O que ainda é evolução natural, não bloqueio de deploy:

- integração final do sensor físico;
- layout final para visor local do protótipo;
- alertas sonoros via hardware;
- endurecimento de produção com observabilidade e rotação de segredos.
