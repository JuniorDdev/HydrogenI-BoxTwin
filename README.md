# BoxTwin 3D — MVP autônomo com Raspberry Pi

Primeira estrutura executável do projeto HydrogenI para o Hackathon do Complexo Portuário do Itaqui 2026.

## Escopo deste incremento

- Raspberry Pi 4 (4 GB) ou Raspberry Pi 5 como servidor de borda;
- sensor VL53L5CX 8×8, representado por uma interface substituível;
- modo simulado para desenvolvimento sem hardware;
- calibração do box vazio;
- cálculo de volume por grade de 64 células;
- índice simples de confiança;
- histórico em SQLite;
- API Flask e TwinBoard responsivo;
- alertas de capacidade, baixa confiança e sensor obstruído;
- operação local/offline.

## Arquitetura

```text
VL53L5CX 8×8 -> SensorService -> VolumeService -> SQLite
                                      |
                                      +-> AlertService
                                      +-> API Flask -> TwinBoard
```

Cada instalação representa um **BoxNode**. A mesma aplicação poderá cadastrar outros nós no futuro.

## Execução rápida no computador ou Raspberry Pi

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

No Windows, ative com `.venv\Scripts\activate`. Acesse `http://127.0.0.1:5000`.

O modo inicial é `SENSOR_MODE=mock`, portanto funciona sem sensor. Para simular diferentes cargas:

```bash
curl -X POST http://127.0.0.1:5000/api/demo/level/75
```

## Calibração

1. Deixe a maquete vazia.
2. Abra o TwinBoard.
3. Clique em **Calibrar box vazio**.
4. Adicione um volume conhecido e compare o volume indicado.

O cálculo usado em cada célula é:

```text
altura_da_carga = distância_box_vazio - distância_atual
volume_da_célula = altura_da_carga × área_da_célula
volume_total = soma das 64 células válidas
```

## Configurações principais

Edite `.env`:

- `BOX_LENGTH_M` e `BOX_WIDTH_M`: dimensões internas da base da maquete;
- `BOX_HEIGHT_M`: altura útil até o sensor;
- `SAMPLE_INTERVAL_SECONDS`: intervalo automático entre leituras;
- `CAPACITY_ALERT_PERCENT`: limite de capacidade;
- `MIN_CONFIDENCE_PERCENT`: confiança mínima;
- `SENSOR_MODE`: `mock` ou `vl53l5cx`.

## Sensor físico

O arquivo `boxtwin/sensors/vl53l5cx.py` é o ponto único de integração. O adaptador real deverá retornar uma matriz 8×8 em milímetros. A biblioteca/driver exato dependerá da placa breakout adquirida e do pacote recomendado pelo fabricante.

## Testes

```bash
pytest -q
```

## Próximos incrementos

1. Conectar e validar o VL53L5CX físico via I²C.
2. Fazer cinco capturas na calibração e aplicar mediana por célula.
3. Incluir MQTT e sincronização posterior com servidor central.
4. Representar a superfície como malha 3D no TwinBoard.
5. Validar três níveis de carga e calcular erro contra volumes conhecidos.

