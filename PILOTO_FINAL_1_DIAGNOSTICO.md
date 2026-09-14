# Piloto final 1 — diagnóstico e implantação

## Componentes reaproveitados

O BoxTwin já processa a matriz 8×8 no Raspberry por meio do adaptador `VL53L8CX`, mantém o modo `mock`, calcula volume/confiança/ocupação em `VolumeService`, grava leituras no SQLite e usa `reading_uuid` único. A tabela `sync_queue` conserva leituras pendentes e a API central `POST /api/edge/readings` é idempotente: um reenvio retorna sucesso sem duplicar a leitura.

O sistema também já possui grade ao vivo (`live_sensor_grids`), envio de grade, SSE para atualização de páginas, relatórios, notificações e configuração por `.env`. O processamento físico permanece no BoxNode; o Railway recebe somente resultados processados e a telemetria.

## Alterações deste piloto

- `boxtwin/config.py`: heartbeat, prazo para considerar node offline e mapa opcional de tokens por node.
- `boxtwin/database.py`: tabela `box_nodes` e consulta de estado por node. As tabelas existentes `readings`, `sync_queue` e `live_sensor_grids` continuam sendo usadas.
- `boxtwin/services.py` e `boxtwin/runtime.py`: envio periódico de heartbeat pelo Raspberry, sem interromper captura, fila local ou operação offline.
- `boxtwin/routes.py`: `POST /api/edge/heartbeat`, `GET /api/boxes/<node_id>`, `GET /box/<node_id>` e SSE filtrável por `node_id`.
- `boxtwin/templates/box_monitor.html` e `boxtwin/static/box-monitor.js`: painel online do BoxNode.

O banco é migrado automaticamente pela inicialização do projeto. Nenhuma tabela existente é removida.

## Autenticação e sincronização

No Raspberry, `EDGE_SYNC_TOKEN` é o segredo daquele node. No Railway, o segredo pode ser configurado globalmente com `EDGE_SYNC_TOKEN` durante o piloto, ou por node com:

```env
EDGE_NODE_TOKENS={"BOX-01":"troque-por-um-segredo-longo"}
```

O token nunca é exposto no navegador. A API valida o token antes de aceitar leitura, grade ou heartbeat. A validação por node é genérica e não contém lógica especial para `BOX-01`.

A leitura é persistida primeiro no SQLite local. Depois é colocada em `sync_queue`, com `attempts`, `last_attempt_at`, `last_error`, `synced_at` e `status`. O loop de manutenção tenta os itens pendentes em lotes; se a internet falhar, a fila é preservada. A próxima execução tenta novamente, sem criar duplicidade no Railway.

## Heartbeat e tela central

O Raspberry envia `POST /api/edge/heartbeat` a cada `HEARTBEAT_INTERVAL_SECONDS` (padrão: 30). O Railway marca o node como offline depois de `NODE_OFFLINE_AFTER_SECONDS` (padrão: 120) sem sinal. A tela:

```text
/box/BOX-01
```

mostra estado do node, sensor, última sincronização e última leitura. Ela usa SSE para reagir a uma leitura nova e polling controlado como fallback para o estado do heartbeat. A matriz 8×8 remota permanece em:

```text
/gemeo-sensor?node_id=BOX-01
```

## Configuração do Raspberry

```env
BOX_NODE_ID=BOX-01
SENSOR_MODE=vl53l8cx
EDGE_SYNC_ENABLED=true
LIVE_SENSOR_SYNC_ENABLED=true
EDGE_SYNC_TARGET_URL=https://SEU-PROJETO.up.railway.app
EDGE_SYNC_TOKEN=troque-por-um-segredo-longo
HEARTBEAT_INTERVAL_SECONDS=30
NODE_OFFLINE_AFTER_SECONDS=120
```

No Railway, configure o mesmo segredo em `EDGE_NODE_TOKENS` ou, apenas enquanto houver uma box, em `EDGE_SYNC_TOKEN`. No Railway, mantenha `SENSOR_MODE=mock`: ele não acessa o hardware.

## Riscos e validação

O SSE pode sofrer limitação de conexão persistente em alguns proxies; por isso as páginas também atualizam por polling. O `sync_queue` atual tenta de novo a cada ciclo de manutenção e evita loop apertado pelo intervalo configurável; um backoff exponencial por item é a evolução indicada caso o volume de boxes cresça.

Teste de aceitação: capturar com internet ativa; desligar a internet; gerar leituras; confirmar que a fila cresce no Raspberry; religar; confirmar que as pendências sincronizam uma vez; abrir `/box/BOX-01` e verificar que o node volta para `ONLINE`.
