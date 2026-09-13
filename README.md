# HydrogenI BoxTwin 3D

MVP para medição e monitoramento do volume de fertilizante armazenado em boxes. A aplicação recebe
uma matriz de profundidade 8×8, reconstrói a superfície da carga, calcula volume e ocupação, mantém
histórico operacional e gera alertas com tratativa rastreável.

O projeto funciona hoje em modo simulado e está preparado para operar no Raspberry Pi como nó local,
armazenar leituras durante quedas de internet e sincronizá-las com a aplicação hospedada no Railway.

## Protótipo físico recomendado

Para a bancada do MVP com sensor ToF 8×8, a configuração recomendada é:

```text
Área interna: 40 cm × 40 cm
Altura interna útil: 40 cm
Capacidade geométrica: 64 litros
Altura máxima de material nos testes: 30 cm
Capacidade operacional de teste: 48 litros
Sensor centralizado, apontado para baixo, a 70–80 cm do fundo interno
```

Essa dimensão melhora a resolução por zona do sensor: cada célula da matriz 8×8 representa
aproximadamente 5 cm × 5 cm da superfície. As instruções de corte e montagem estão em
[PROTOTIPO_MDF.md](PROTOTIPO_MDF.md).

## Fluxo da solução

```text
Box → sensor 8×8 → Raspberry/Edge → cálculo volumétrico → SQLite/fila offline
                                                        ↓
                               Railway ← sincronização ← internet disponível
                                  ↓
                    painel, alertas, e-mail e relatórios
```

## Funcionalidades atuais

- simulador com nove cenários de carga e falha;
- gêmeo digital 3D e mapa de altura 8×8;
- volume em m³, ocupação, alturas média/máxima e confiança;
- alertas de capacidade, baixa confiança e possível obstrução;
- confirmação humana, fila operacional e arquivamento das tratativas;
- histórico de notificações com diagnóstico de falha do provedor;
- destinatários e regras de escalonamento por anomalia;
- relatórios operacionais em PDF e Excel;
- RAG local com Groq opcional e fallback offline;
- SQLite local, retenção automática e fila de sincronização Edge → Railway;
- ingestão idempotente por `reading_uuid`, evitando leituras duplicadas;
- painel responsivo, atualização via SSE e suporte PWA.

## Estado do sensor físico

O modo funcional atual é:

```env
SENSOR_MODE=mock
```

Os adaptadores `vl53l5cx` e `vl53l8cx` já reservam o ponto de integração em
`boxtwin/sensors/`, mas ainda precisam receber o driver e a leitura real do hardware. Portanto, os
resultados do simulador demonstram o fluxo do produto, não a precisão final do sensor físico.

## Execução local

### Windows / PowerShell

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

### Linux / Raspberry Pi

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Acesse:

- projeto: `http://127.0.0.1:5000/`;
- simulador: `http://127.0.0.1:5000/simulador`;
- aplicativo móvel/PWA: `http://127.0.0.1:5000/app`;
- administração: `http://127.0.0.1:5000/admin`;
- saúde da aplicação: `http://127.0.0.1:5000/api/health`.

O guia completo do nó local está em [README_RASPBERRY.md](README_RASPBERRY.md).

## Railway

O Railway executa o comando definido em `railway.json`, usando Gunicorn e a porta fornecida na
variável `PORT`. Configure um volume persistente para o diretório `data/` para preservar o SQLite
entre deploys.

Variáveis essenciais no Railway:

```env
APP_HOST=0.0.0.0
APP_DEBUG=false
SENSOR_MODE=mock
BOX_LENGTH_M=0.40
BOX_WIDTH_M=0.40
BOX_HEIGHT_M=0.40
DATABASE_PATH=data/boxtwin.db
CALIBRATION_PATH=data/calibration.json
SECRET_KEY=gere-uma-chave-longa-e-aleatoria
ADMIN_USERNAME=admin
ADMIN_PASSWORD=troque-por-uma-senha-forte
PUBLIC_BASE_URL=https://seu-projeto.up.railway.app

EMAIL_ENABLED=true
RESEND_API_KEY=re_chave_real
RESEND_FROM_EMAIL=remetente-de-dominio-verificado@seudominio.com
ALERT_EMAIL_TO=destinatario@exemplo.com

GROQ_ENABLED=true
GROQ_API_KEY=gsk_chave_real
GROQ_MODEL=openai/gpt-oss-120b

EDGE_SYNC_ENABLED=false
LIVE_SENSOR_SYNC_ENABLED=false
EDGE_SYNC_TOKEN=mesmo-token-secreto-configurado-no-raspberry
```

O Railway injeta `PORT` automaticamente. Não versione `.env`, chaves ou senhas. Consulte
[DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md) para o processo completo.

## Variáveis reconhecidas

| Grupo | Variáveis |
|---|---|
| Aplicação | `APP_HOST`, `APP_PORT`, `PORT`, `APP_DEBUG`, `PUBLIC_BASE_URL` |
| Box/sensor | `SENSOR_MODE`, `BOX_NODE_ID`, `BOX_NAME`, `BOX_LENGTH_M`, `BOX_WIDTH_M`, `BOX_HEIGHT_M`, `SAMPLE_INTERVAL_SECONDS` |
| Alertas | `CAPACITY_ALERT_PERCENT`, `MIN_CONFIDENCE_PERCENT`, `NOTIFY_COOLDOWN_SECONDS` |
| Persistência | `DATABASE_PATH`, `CALIBRATION_PATH` |
| Segurança | `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` |
| Resend | `EMAIL_ENABLED`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `ALERT_EMAIL_TO` |
| Twilio | `TWILIO_ENABLED`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM`, `TWILIO_TO`, `TWILIO_VALIDATE_SIGNATURE` |
| Assistente | `GROQ_ENABLED`, `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_TIMEOUT_SECONDS` |
| Edge sync | `EDGE_SYNC_ENABLED`, `LIVE_SENSOR_SYNC_ENABLED`, `EDGE_SYNC_TARGET_URL`, `EDGE_SYNC_TOKEN`, `EDGE_SYNC_TIMEOUT_SECONDS`, `EDGE_SYNC_BATCH_SIZE` |
| Retenção | `AUTO_CLEANUP_ENABLED`, `READINGS_RETENTION_DAYS`, `NOTIFICATIONS_RETENTION_DAYS`, `INCIDENTS_RETENTION_DAYS`, `SYNC_QUEUE_RETENTION_DAYS` |

## Gêmeo 3D do sensor sem calibração

Em um BoxNode físico, configure `LIVE_SENSOR_SYNC_ENABLED=true` junto com a sincronização de borda. O Raspberry envia a matriz bruta 8 × 8 periodicamente para o Railway, sem calcular volume ou criar alertas. A visualização remota fica em `/gemeo-sensor` e mostra proximidade relativa ao sensor.

## Testes

```bash
pytest -q
```

A suíte cobre volume, API, autenticação administrativa, anomalias, relatórios e prevenção de regras
de notificação duplicadas. Serviços externos permanecem desativados durante os testes.

## Segurança

- nunca publique `.env`, tokens ou chaves de API;
- use valores diferentes para `SECRET_KEY` e `EDGE_SYNC_TOKEN`;
- rotacione imediatamente qualquer credencial exposta;
- troque a senha administrativa antes do deploy;
- use domínio verificado na Resend para enviar a destinatários externos;
- mantenha a decisão e a intervenção operacional sob responsabilidade humana.

## Limite do MVP

A arquitetura de software está pronta para a integração física, mas a precisão industrial só poderá
ser declarada após instalação do sensor, calibração do box vazio e comparação com volumes físicos
conhecidos em condições reais de poeira, vibração e movimentação de máquinas.
