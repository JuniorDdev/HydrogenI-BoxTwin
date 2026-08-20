# README Raspberry Pi - HydrogenI BoxTwin 3D

Este guia foi escrito para preparar o `HydrogenI-BoxTwin` no Raspberry Pi como runtime local do
BoxNode, mantendo o painel disponível na rede local e, opcionalmente, sincronizando leituras com o
Railway quando houver internet.

## Objetivo desta instalação

No Raspberry, o sistema pode operar como:

- origem local das leituras do BoxNode;
- painel acessível na rede interna;
- armazenamento local em SQLite;
- ponto de sincronização com o Railway;
- base pronta para troca de `mock` para sensor físico depois.

## Pré-requisitos

- Raspberry Pi com Raspberry Pi OS atualizado;
- Python 3.11+ disponível;
- Git instalado;
- acesso à rede local;
- driver do sensor já preparado ou, por enquanto, uso em `SENSOR_MODE=mock`;
- pasta de destino no Raspberry, por exemplo: `/opt/boxtwin`.

## Clonar o projeto

```bash
cd /opt
sudo git clone https://github.com/JuniorDdev/HydrogenI-BoxTwin.git boxtwin
sudo chown -R pi:pi /opt/boxtwin
cd /opt/boxtwin
```

Se você já estiver usando outra branch local de trabalho, ajuste o `git checkout` conforme sua
estratégia.

## Ambiente virtual

```bash
cd /opt/boxtwin
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Arquivo .env no Raspberry

Crie o arquivo:

```bash
cp .env.example .env
```

Exemplo de `.env` local para Raspberry operando em rede interna e sincronizando com o Railway:

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
RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=onboarding@resend.dev

TWILIO_ENABLED=false
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM=
TWILIO_TO=
TWILIO_VALIDATE_SIGNATURE=true

PUBLIC_BASE_URL=https://hydrogeni-boxtwin-production.up.railway.app/

GROQ_ENABLED=true
GROQ_API_KEY=gsk_...
GROQ_MODEL=openai/gpt-oss-120b

EDGE_SYNC_ENABLED=true
EDGE_SYNC_TARGET_URL=https://hydrogeni-boxtwin-production.up.railway.app
EDGE_SYNC_TOKEN=um-token-longo-e-unico
EDGE_SYNC_TIMEOUT_SECONDS=15
EDGE_SYNC_BATCH_SIZE=20

AUTO_CLEANUP_ENABLED=true
READINGS_RETENTION_DAYS=45
NOTIFICATIONS_RETENTION_DAYS=60
INCIDENTS_RETENTION_DAYS=180
SYNC_QUEUE_RETENTION_DAYS=7
```

## Observações importantes sobre o .env

- `EMAIL_ENABLED` precisa ser `true`, `false`, `yes`, `on` ou `1`.
- `PUBLIC_BASE_URL` no Raspberry pode continuar apontando para o domínio do Railway quando o foco for
  comunicação central e links públicos.
- `EDGE_SYNC_ENABLED=true` ativa a fila local e o reenvio para o Railway.
- `EDGE_SYNC_TOKEN` deve ser exatamente o mesmo no Raspberry e no Railway.
- Para trocar para sensor real depois, a variável será:

```env
SENSOR_MODE=vl53l8cx
```

## Rodar manualmente

```bash
cd /opt/boxtwin
source .venv/bin/activate
python app.py
```

Depois acesse:

- `http://IP_DO_RASPBERRY:5000/`
- `http://IP_DO_RASPBERRY:5000/simulador`
- `http://IP_DO_RASPBERRY:5000/admin`

## Rodar como serviço systemd

O projeto já possui um exemplo em:

- `systemd/boxtwin.service`

No Raspberry, copie para o systemd:

```bash
sudo cp systemd/boxtwin.service /etc/systemd/system/boxtwin.service
sudo systemctl daemon-reload
sudo systemctl enable boxtwin
sudo systemctl start boxtwin
```

Verificar status:

```bash
sudo systemctl status boxtwin
```

Ver logs:

```bash
journalctl -u boxtwin -f
```

## Sincronização Raspberry -> Railway

Quando `EDGE_SYNC_ENABLED=true`, cada leitura:

1. é salva primeiro no SQLite local;
2. entra na fila de sincronização local;
3. tenta ser enviada para o Railway;
4. se falhar, permanece pendente para nova tentativa;
5. quando a conexão voltar, o sistema reenfileira e envia sem duplicação.

O endpoint central usa `reading_uuid` para ingestão idempotente.

## Limpeza automática

O runtime já executa limpeza automática diária quando `AUTO_CLEANUP_ENABLED=true`.

Política inicial recomendada:

- `READINGS_RETENTION_DAYS=45`
- `NOTIFICATIONS_RETENTION_DAYS=60`
- `INCIDENTS_RETENTION_DAYS=180`
- `SYNC_QUEUE_RETENTION_DAYS=7`

Com isso:

- leituras antigas saem do Raspberry;
- notificações antigas são removidas;
- incidentes resolvidos podem ser mantidos por mais tempo;
- a fila sincronizada não cresce indefinidamente.

## Testes locais

```bash
cd /opt/boxtwin
source .venv/bin/activate
pytest -q
```

## O que já está pronto no Raspberry

- painel e simulador na rede local;
- leitura contínua em `mock`;
- fila local de sincronização com o Railway;
- retenção automática;
- alertas com tratativa;
- relatórios PDF e Excel;
- base pronta para sensor físico.

## O que ainda depende do hardware real

- integração final do adaptador `vl53l8cx`;
- validação de precisão física;
- saída sonora/luminosa por GPIO, se desejado no protótipo final.
