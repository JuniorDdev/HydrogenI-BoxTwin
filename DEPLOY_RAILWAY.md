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
BOX_NAME=BoxTwin 3D - prototipo MDF 40x40
BOX_LENGTH_M=0.40
BOX_WIDTH_M=0.40
BOX_HEIGHT_M=0.40
SAMPLE_INTERVAL_SECONDS=15
CAPACITY_ALERT_PERCENT=85
MIN_CONFIDENCE_PERCENT=70
EMAIL_ENABLED=false
TWILIO_ENABLED=false
GROQ_ENABLED=false
TWILIO_VALIDATE_SIGNATURE=true
```

Não defina `PORT`; o Railway fornece essa variável automaticamente.

Depois de gerar o domínio público, acrescente:

```env
PUBLIC_BASE_URL=https://SEU-DOMINIO.up.railway.app
```

Ative Groq, Twilio e e-mail separadamente somente depois de validar painel, login, banco e Volume.

## Verificação

```text
https://SEU-DOMINIO/api/health
https://SEU-DOMINIO/
https://SEU-DOMINIO/simulador
https://SEU-DOMINIO/admin
```

O `manifest.webmanifest` está incluído em `boxtwin/static`, permitindo que o Service Worker conclua o cache inicial da PWA.
