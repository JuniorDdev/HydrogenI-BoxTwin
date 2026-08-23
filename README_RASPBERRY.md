# Configuração do Raspberry Pi — HydrogenI BoxTwin

Este guia prepara o Raspberry Pi para atuar como BoxNode local: capturar leituras, manter o painel na
rede interna, persistir dados offline e sincronizar com o Railway quando a internet voltar.

## Arquitetura recomendada

```text
Sensor → Raspberry Pi → SQLite + fila local → Railway
                │              conexão retorna ↗
                └→ painel local: http://IP_DO_RASPBERRY:5000
```

O Raspberry continua funcionando sem internet. O Railway centraliza dados sincronizados,
notificações ao cliente e relatórios consolidados.

## 1. Preparar o sistema

Recomendado: Raspberry Pi 4 ou 5, Raspberry Pi OS 64-bit, Python 3.11+, rede e fonte estáveis.

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y git python3 python3-venv python3-pip
sudo timedatectl set-timezone America/Sao_Paulo
```

## 2. Clonar a `main`

```bash
cd /opt
sudo git clone --branch main https://github.com/JuniorDdev/HydrogenI-BoxTwin.git boxtwin
sudo chown -R "$USER":"$USER" /opt/boxtwin
cd /opt/boxtwin
```

Para atualizar depois:

```bash
cd /opt/boxtwin
git pull --ff-only origin main
```

## 3. Instalar as dependências

```bash
cd /opt/boxtwin
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Criar o `.env.raspberry`

```bash
nano /opt/boxtwin/.env.raspberry
```

Modelo compatível com o código atual:

```env
APP_HOST=0.0.0.0
APP_PORT=5000
APP_DEBUG=false

SENSOR_MODE=mock
BOX_NODE_ID=BOX-RASP-01
BOX_NAME=BoxTwin 3D - prototipo MDF 40x40
BOX_LENGTH_M=0.40
BOX_WIDTH_M=0.40
BOX_HEIGHT_M=0.40
SAMPLE_INTERVAL_SECONDS=5
CAPACITY_ALERT_PERCENT=85
MIN_CONFIDENCE_PERCENT=70

DATABASE_PATH=data/boxtwin.db
CALIBRATION_PATH=data/calibration.json

SECRET_KEY=gere-uma-chave-exclusiva-para-o-raspberry
ADMIN_USERNAME=admin
ADMIN_PASSWORD=troque-por-uma-senha-forte

NOTIFY_COOLDOWN_SECONDS=300
EMAIL_ENABLED=false
RESEND_API_KEY=
RESEND_FROM_EMAIL=
ALERT_EMAIL_TO=

TWILIO_ENABLED=false
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM=
TWILIO_TO=
TWILIO_VALIDATE_SIGNATURE=true

PUBLIC_BASE_URL=http://IP_DO_RASPBERRY:5000

GROQ_ENABLED=false
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b
GROQ_TIMEOUT_SECONDS=20

EDGE_SYNC_ENABLED=true
EDGE_SYNC_TARGET_URL=https://hydrogeni-boxtwin-production.up.railway.app
EDGE_SYNC_TOKEN=mesmo-token-secreto-configurado-no-railway
EDGE_SYNC_TIMEOUT_SECONDS=15
EDGE_SYNC_BATCH_SIZE=20

AUTO_CLEANUP_ENABLED=true
READINGS_RETENTION_DAYS=45
NOTIFICATIONS_RETENTION_DAYS=60
INCIDENTS_RETENTION_DAYS=180
SYNC_QUEUE_RETENTION_DAYS=7
```

Substitua `IP_DO_RASPBERRY`, `SECRET_KEY`, `ADMIN_PASSWORD` e `EDGE_SYNC_TOKEN`. O token Edge precisa
ser exatamente igual ao configurado no Railway. Use `EDGE_SYNC_ENABLED=false` no Railway e `true` no
Raspberry.

O e-mail fica desativado no Raspberry para evitar alertas duplicados. O Railway envia as notificações
após receber as leituras sincronizadas. O RAG local funciona com `GROQ_ENABLED=false`, inclusive
offline.

Para o protótipo de bancada recomendado, use área interna de 40 cm × 40 cm e altura útil de 40 cm.
Isso representa 0,064 m³, ou 64 litros de capacidade geométrica. Para preservar distância segura até
o sensor, limite os testes práticos a 30 cm de material, equivalentes a 48 litros.

## 5. Testar manualmente

O `python-dotenv` procura um arquivo chamado `.env`. Crie um link local para o arquivo específico:

```bash
cd /opt/boxtwin
ln -sfn .env.raspberry .env
source .venv/bin/activate
python app.py
```

Teste localmente:

```bash
curl http://127.0.0.1:5000/api/health
```

Na rede interna, acesse:

- `http://IP_DO_RASPBERRY:5000/`;
- `http://IP_DO_RASPBERRY:5000/simulador`;
- `http://IP_DO_RASPBERRY:5000/app`;
- `http://IP_DO_RASPBERRY:5000/admin`.

## 6. Instalar como serviço

`systemd/boxtwin.service` usa Gunicorn com um worker e oito threads. O worker único evita que a rotina
de captura em segundo plano seja iniciada mais de uma vez.

Confira o usuário:

```bash
whoami
```

Se ele não for `pi`, altere `User=` e `Group=` em `systemd/boxtwin.service` antes de copiar.

```bash
cd /opt/boxtwin
sudo cp systemd/boxtwin.service /etc/systemd/system/boxtwin.service
sudo systemctl daemon-reload
sudo systemctl enable --now boxtwin
sudo systemctl status boxtwin
```

Logs e reinicialização:

```bash
journalctl -u boxtwin -f
sudo systemctl restart boxtwin
```

## 7. Reservar o IP local

Prefira uma reserva DHCP no roteador. Para consultar IP e interfaces:

```bash
hostname -I
ip link
```

Não exponha a porta `5000` diretamente à internet. Use o Railway ou uma VPN administrada para acesso
externo.

## 8. Operação offline e sincronização

Para cada captura, o runtime:

1. grava a leitura no SQLite local;
2. cria um `reading_uuid` único;
3. adiciona a leitura à fila;
4. tenta enviar para `/api/edge/readings` no Railway;
5. mantém a leitura pendente se a internet cair;
6. tenta novamente quando a conexão retornar;
7. usa o UUID para evitar duplicação no Railway.

O estado da fila está disponível, após autenticação administrativa, em:

```text
GET /api/admin/sync-status
```

Resposta HTTP `401` na sincronização normalmente significa tokens Edge diferentes.

## 9. Retenção e armazenamento

```env
AUTO_CLEANUP_ENABLED=true
READINGS_RETENTION_DAYS=45
NOTIFICATIONS_RETENTION_DAYS=60
INCIDENTS_RETENTION_DAYS=180
SYNC_QUEUE_RETENTION_DAYS=7
```

A limpeza preserva leituras pendentes ou com falha de sincronização. Monitore o armazenamento:

```bash
df -h
du -h /opt/boxtwin/data/*
```

## 10. Integração futura do VL53L8CX

Até o driver real ser implementado, mantenha:

```env
SENSOR_MODE=mock
```

`boxtwin/sensors/vl53l8cx.py` ainda é um adaptador reservado. Quando o hardware chegar:

1. instale e valide o driver da placa utilizada;
2. habilite I²C/SPI e ajuste permissões;
3. implemente `read_distance_grid_mm()` retornando uma matriz 8×8 em milímetros;
4. represente zonas inválidas como `None`;
5. calibre com o box vazio;
6. compare com volumes físicos conhecidos;
7. altere para `SENSOR_MODE=vl53l8cx` somente depois da validação.

## 11. Diagnóstico rápido

```bash
sudo systemctl status boxtwin
journalctl -u boxtwin -n 100 --no-pager
ss -lntp | grep 5000
hostname -I
```

- painel inacessível: confira `APP_HOST=0.0.0.0`, IP e porta;
- sincronização 401: confira `EDGE_SYNC_TOKEN` nos dois ambientes;
- fila não diminui: confira internet, URL do Railway e logs;
- serviço não inicia: confira usuário, caminhos e conteúdo do `.env.raspberry`.

## Checklist

- [ ] painel abre pela rede local;
- [ ] `.env.raspberry` não está versionado;
- [ ] senha administrativa foi alterada;
- [ ] `SECRET_KEY` e `EDGE_SYNC_TOKEN` são diferentes;
- [ ] token Edge é igual ao do Railway;
- [ ] cenário mock gera leitura e histórico;
- [ ] queda de internet mantém leituras pendentes;
- [ ] reconexão envia sem duplicar;
- [ ] serviço inicia após reboot;
- [ ] armazenamento e logs foram verificados.
