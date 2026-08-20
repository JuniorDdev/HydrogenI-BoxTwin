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
- notificações opcionais por e-mail (Resend) e Twilio (SMS ou WhatsApp Sandbox);
- assistente local com RAG sobre procedimentos em `boxtwin/knowledge/procedures.json`;
- PWA responsiva para Android e contrato JSON reutilizável por um futuro app Flutter.
- cadastro de responsáveis individuais ou equipes;
- regras por anomalia, severidade, canal e tempo de escalonamento;
- Groq (GroqCloud) com fallback automático para o RAG local;
- página detalhada de cada incidente, evidências e linha do tempo;
- estados `aberta`, `ciente`, `em atendimento`, `resolvida` e `falso positivo`;
- webhooks Twilio para status de entrega e respostas `1 ID`, `2 ID` ou `3 ID`.
- landing page institucional em `/`, simulador independente em `/simulador` e painel real em `/admin`;
- relatório operacional em PDF com indicadores, leituras recentes, incidentes e nota sobre o modo simulado;
- atalhos de perguntas no assistente e contexto automático da última leitura e das anomalias ativas.

No primeiro acesso local, use `admin` / `HydrogenI@2026` e altere ambos no `.env` antes de qualquer publicação. Para produção, use uma senha forte e uma `SECRET_KEY` aleatória. O RAG atual é deliberadamente local e baseado em recuperação; um provedor de LLM pode ser conectado depois sem mudar a interface administrativa.

Para o Twilio, cadastre os webhooks públicos em `/api/webhooks/twilio/incoming` (mensagens recebidas) e `/api/webhooks/twilio/status` (status). O endereço de `PUBLIC_BASE_URL` deve coincidir exatamente com o domínio HTTPS informado ao Twilio para a validação de assinatura funcionar.
