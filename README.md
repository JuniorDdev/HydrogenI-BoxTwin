# HydrogenI BoxTwin 3D

Aplicação Flask que mede o volume de fertilizante armazenado em um box a partir de uma matriz de profundidade 8×8, mantém um gêmeo digital 3D dessa carga no navegador e opera uma central administrativa com fila de anomalias, notificações e um assistente técnico. Funciona hoje inteiramente em modo simulado (sem hardware) e foi desenhada para trocar o sensor virtual pelo sensor físico sem mudar cálculo, API, banco ou painel.

## Arquitetura

```
BoxNode                Edge                      VolumeCore              TwinBoard
(sensor)         →     (runtime local)      →     (cálculo)         →    (interface web)

grid 8x8 mm             BoxTwinRuntime             VolumeService          landing (/)
distâncias        →     captura, agenda,     →     altura por zona  →     simulador (/simulador)
                         alerta, notifica,          volume, ocupação       admin (/admin)
mock | VL53L5CX |        grava no SQLite            confiança, zonas       API JSON (/api/*)
VL53L8CX (futuro)        RAG/Groq                   válidas
```

- **BoxNode** — a fonte da matriz de distâncias 8×8 em milímetros. Hoje é o `MockSensor`
  (`boxtwin/sensors/mock.py`), que simula 9 cenários de carga. Os pontos de integração para
  hardware físico já existem em `boxtwin/sensors/vl53l5cx.py` e `boxtwin/sensors/vl53l8cx.py` —
  ambos implementam a mesma interface `DepthSensor` (`boxtwin/sensors/base.py`) e hoje só levantam
  `RuntimeError` avisando que o driver ainda não foi conectado.
- **Edge** — o processo Flask rodando localmente (PC de demonstração ou Raspberry Pi), orquestrado
  por `BoxTwinRuntime` (`boxtwin/runtime.py`): captura periódica, avaliação de alertas, gravação em
  SQLite (`boxtwin/database.py`), disparo de notificações (`NotificationService`) e resposta do
  assistente técnico (`RagService`/`GroqService`), tudo em `boxtwin/services.py`.
- **VolumeCore** — o cálculo puro em `VolumeService` (`boxtwin/services.py`): transforma a matriz de
  distâncias em altura por zona, soma o volume, calcula ocupação, altura média/máxima e um índice de
  confiança baseado em quantas das 64 zonas retornaram leitura válida.
- **TwinBoard** — a interface web: landing institucional (`/`), simulador com o gêmeo digital 3D em
  Canvas e os 9 cenários de demonstração (`/simulador`), e a central administrativa autenticada com
  fila de anomalias, notificações, cadastro de responsáveis/regras e assistente técnico (`/admin`).

O mesmo fluxo de cálculo, banco, API e painel atende tanto o sensor virtual quanto o físico — trocar
`SENSOR_MODE` no `.env` é a única mudança necessária quando o driver do VL53L8CX estiver pronto.

## Estado atual

**Pronto e demonstrável hoje (modo `mock`, sem hardware):**

- 9 cenários de simulação: vazio, carga uniforme 25/50/75%, quase cheio, pilha central, superfície
  inclinada, carga irregular e sensor parcialmente obstruído (`boxtwin/sensors/mock.py`);
- cálculo de volume, ocupação, altura média/máxima e confiança a partir da matriz 8×8;
- gêmeo digital 3D em Canvas puro (sem bibliotecas externas), com histórico de ocupação em gráfico;
- painel administrativo autenticado: fila de anomalias com ciência/atendimento/resolução, página de
  detalhe com linha do tempo, cadastro de responsáveis/equipes e regras de escalonamento por canal;
- notificações opcionais por e-mail (API da Resend) e Twilio (SMS/WhatsApp Sandbox), com
  antirrepetição e webhooks de status/resposta;
- assistente técnico em balão flutuante: RAG local sobre `boxtwin/knowledge/procedures.json`, com
  fallback automático, e integração opcional com a Groq (GroqCloud) para respostas mais naturais,
  mantendo o histórico da conversa e sempre citando as fontes (`PROC-XXX`);
- relatório operacional em PDF (indicadores, leituras recentes, incidentes);
- atualização em tempo real via Server-Sent Events, PWA instalável e histórico local em SQLite.

**Depende do sensor físico (VL53L8CX ainda não integrado):**

- os adaptadores `VL53L5CXSensor` e `VL53L8CXSensor` (`boxtwin/sensors/`) são apenas pontos de
  integração reservados — hoje levantam erro ao serem instanciados, porque nenhum driver do
  fabricante foi conectado ainda;
- os números do modo `mock` demonstram o método matemático e a experiência operacional, mas não são
  uma validação de precisão de sensor real — isso só é possível depois de medir volumes físicos
  conhecidos com o hardware instalado;
- quando o driver existir, a mudança é apenas `SENSOR_MODE=vl53l8cx` no `.env`: cálculo, API, banco
  de dados e painel não precisam ser alterados.

## Como rodar localmente

### Windows

No terminal do VS Code (PowerShell), dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Se o PowerShell bloquear a ativação do ambiente virtual, rode uma vez:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Linux ou Raspberry Pi

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Para manter o BoxNode rodando como serviço no Raspberry Pi, use o arquivo de exemplo
`systemd/boxtwin.service` (ajuste `WorkingDirectory` e instale em `/etc/systemd/system/`).

### Depois de subir

Acesse `http://127.0.0.1:5000`. A página inicial (`/`) apresenta o projeto, o simulador fica em
`/simulador` e a central administrativa autenticada em `/admin` (login padrão `admin` /
`HydrogenI@2026` — troque os dois no `.env` antes de qualquer publicação).

## Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste conforme o ambiente. Nada além do `.env.example` deve ser
versionado — o `.env` real fica fora do controle de versão.

### Aplicação e box físico

| Variável | Para que serve | Padrão |
|---|---|---|
| `APP_HOST` | Endereço em que o Flask escuta | `0.0.0.0` |
| `APP_PORT` / `PORT` | Porta HTTP (Railway injeta `PORT` automaticamente) | `5000` |
| `APP_DEBUG` | Ativa o modo debug do Flask | `false` |
| `SENSOR_MODE` | `mock` (virtual), `vl53l5cx` ou `vl53l8cx` (hardware físico, ainda não integrado) | `mock` |
| `BOX_NODE_ID` | Identificador do BoxNode exibido no painel | `BOX-DEMO-01` |
| `BOX_NAME` | Nome amigável do box | `Box reduzido HydrogenI` |
| `BOX_LENGTH_M` / `BOX_WIDTH_M` / `BOX_HEIGHT_M` | Dimensões internas úteis do box; a capacidade é `comprimento × largura × altura` | `0.60` / `0.40` / `0.50` |
| `SAMPLE_INTERVAL_SECONDS` | Intervalo entre capturas automáticas do BoxNode | `5` |
| `CAPACITY_ALERT_PERCENT` | Ocupação (%) a partir da qual dispara alerta de capacidade | `85` |
| `MIN_CONFIDENCE_PERCENT` | Confiança (%) mínima antes de alertar baixa confiança | `70` |
| `DATABASE_PATH` | Caminho do SQLite (relativo à raiz do projeto) | `data/boxtwin.db` |
| `CALIBRATION_PATH` | Caminho do arquivo de calibração (linha de base vazia) | `data/calibration.json` |

### Autenticação

| Variável | Para que serve | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave de sessão do Flask — troque por um valor aleatório longo antes de publicar | `troque-esta-chave-no-ambiente` |
| `ADMIN_USERNAME` | Usuário da central administrativa | `admin` |
| `ADMIN_PASSWORD` | Senha da central administrativa (texto puro ou hash `pbkdf2`/`scrypt`) | `HydrogenI@2026` |

### Notificações por e-mail (Resend)

| Variável | Para que serve | Padrão |
|---|---|---|
| `EMAIL_ENABLED` | Liga/desliga o canal de e-mail | `false` |
| `RESEND_API_KEY` | Chave da API da [Resend](https://resend.com) usada para enviar os alertas | vazio |
| `RESEND_FROM_EMAIL` | Remetente configurado/verificado na Resend | vazio |
| `ALERT_EMAIL_TO` | Destinatário padrão quando não há responsável cadastrado com regra específica | vazio |

### Notificações por Twilio (SMS/WhatsApp)

| Variável | Para que serve | Padrão |
|---|---|---|
| `TWILIO_ENABLED` | Liga/desliga o canal Twilio | `false` |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` | Credenciais da conta Twilio | vazio |
| `TWILIO_FROM` | Número/remetente Twilio configurado | vazio |
| `TWILIO_TO` | Destinatário padrão quando não há regra específica | vazio |
| `TWILIO_VALIDATE_SIGNATURE` | Valida o header `X-Twilio-Signature` nos webhooks recebidos | `true` |
| `PUBLIC_BASE_URL` | Domínio público HTTPS — precisa bater exatamente com o cadastrado no Twilio | `http://127.0.0.1:5000` |

### Notificações compartilhadas

| Variável | Para que serve | Padrão |
|---|---|---|
| `NOTIFY_COOLDOWN_SECONDS` | Intervalo antirrepetição entre notificações do mesmo tipo de anomalia | `300` |

### Assistente técnico (Groq + RAG local)

| Variável | Para que serve | Padrão |
|---|---|---|
| `GROQ_ENABLED` | Liga/desliga a chamada à API da Groq (GroqCloud); desligado, o assistente usa só o RAG local | `false` |
| `GROQ_API_KEY` | Chave da API da [Groq](https://console.groq.com) | vazio |
| `GROQ_MODEL` | Modelo usado na chamada (formato de chat completions compatível com OpenAI) | `llama-3.3-70b-versatile` |
| `GROQ_TIMEOUT_SECONDS` | Timeout da chamada HTTP à Groq antes de cair no fallback local | `20` |

Sem `GROQ_ENABLED=true` e uma `GROQ_API_KEY` válida, o assistente responde apenas com o RAG local
(recuperação por relevância lexical sobre `boxtwin/knowledge/procedures.json`), o que já funciona
offline e é suficiente para demonstração. Não há mais dependência de SMTP nem da xAI/Grok — os dois
foram substituídos pela Resend e pela Groq, respectivamente.

## API principal

| Método | Rota | Finalidade |
|---|---|---|
| GET | `/api/health` | Estado do BoxNode, dimensões e capacidade |
| GET | `/api/stream` | Eventos em tempo real (SSE) — novas leituras |
| POST | `/api/calibration` | Salva a linha de base do box vazio |
| POST | `/api/readings` | Captura uma nova leitura |
| GET | `/api/readings/latest` | Última leitura registrada |
| GET | `/api/readings/history` | Histórico local de leituras |
| GET | `/api/demo/scenarios` | Lista os 9 cenários de demonstração (modo `mock`) |
| POST | `/api/demo/scenario/<id>` | Aplica um cenário e captura uma leitura |
| POST | `/api/demo/setup` | Calibra vazio e aplica um cenário inicial de demonstração |
| GET | `/api/admin/summary` | Indicadores consolidados do painel administrativo¹ |
| GET | `/api/admin/anomalies` | Fila de anomalias¹ |
| GET | `/api/admin/anomalies/<id>` | Detalhe de uma anomalia (evidências e linha do tempo)¹ |
| POST | `/api/admin/anomalies/<id>/acknowledge` | Registra ciência de uma anomalia¹ |
| POST | `/api/admin/anomalies/<id>/status` | Atualiza o status de uma anomalia¹ |
| GET | `/api/admin/recipients` / POST | Lista ou cadastra responsáveis/equipes¹ |
| GET | `/api/admin/rules` / POST | Lista ou cria regras de notificação/escalonamento¹ |
| GET | `/api/admin/notifications` | Histórico de notificações enviadas¹ |
| POST | `/api/admin/assistant` | Consulta o assistente técnico (RAG local + Groq opcional)¹ |
| GET | `/admin/reports/operational.pdf` | Gera o relatório operacional em PDF¹ |
| POST | `/api/webhooks/twilio/status` | Callback de status de entrega do Twilio |
| POST | `/api/webhooks/twilio/incoming` | Respostas `1 ID` / `2 ID` / `3 ID` recebidas por SMS/WhatsApp |

¹ Rotas protegidas por sessão administrativa (`/login`).

## Testes

```powershell
python -m pytest -q
```

A suíte cobre o cálculo de volume (meia carga, matriz inválida), o motor de alertas, a inicialização
da API, a preparação/troca de cenários de demonstração e o fluxo administrativo (login, fila de
anomalias, assistente, webhooks do Twilio). Os testes isolam explicitamente os canais externos
(`EMAIL_ENABLED`, `TWILIO_ENABLED`, `GROQ_ENABLED` como `False`) para não depender de rede nem do
`.env` local de quem estiver rodando.

## Segurança antes de publicar

- Troque `ADMIN_PASSWORD` e `SECRET_KEY` por valores fortes e aleatórios.
- Mantenha o `.env` fora do controle de versão.
- Use HTTPS e cookies seguros em produção.
- Use credenciais de teste do Twilio antes de habilitar mensagens reais.
- A IA (RAG local ou Groq) nunca aciona máquinas nem decide sozinha — ela só recomenda; a decisão e a
  execução continuam sempre humanas.

## Limite desta versão

Os números no modo `mock` demonstram o método matemático e a experiência operacional do produto, mas
não constituem validação de precisão do sensor real. A margem de erro industrial só poderá ser medida
depois, com o VL53L8CX instalado e volumes físicos conhecidos como referência.
