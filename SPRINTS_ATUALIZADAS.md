# Sprints atualizadas — BoxTwin

Atualizado em 16/09/2026 a partir das entregas do Raspberry Pi 3 B+, VL53L8CX e Railway.

## Sprint 07/09 – 11/09 — Acompanhamento real da BoxNode

**Status: concluída**

- Leitura física do VL53L8CX validada no Raspberry Pi: matriz 8 × 8 com 64 zonas.
- Gêmeo digital 3D e mapa 8 × 8 atualizados com leituras reais.
- Painel mostra status da BoxNode, sensor, última sincronização, volume, ocupação, qualidade das zonas e confiabilidade estimada.
- Persistência local em SQLite, histórico de medições, anomalias e fila de sincronização offline-first.
- Sincronização Raspberry → Railway de medições, grade ao vivo e heartbeat.
- Rotas de captura, calibração e leitura bruta protegidas contra leituras concorrentes do sensor.
- Validação da leitura: o ruído abaixo de 5 mm não é tratado como carga.

## Sprint 14/09 – 18/09 — Operação remota e evolução multi-BoxNode

**Status: em validação integrada**

- Arquitetura por `node_id` consolidada para expansão a BOX-02, BOX-03 e demais unidades.
- Painel por BoxNode em `/box/<node_id>` e gêmeo remoto em `/gemeo-sensor`.
- Comandos remotos para calibrar, capturar, iniciar/retomar e pausar monitoramento.
- Confirmação obrigatória antes de cada comando e intervalo de proteção contra requisições repetidas.
- O monitoramento contínuo é iniciado somente pelo comando **Iniciar/retomar monitoramento**; calibrar e capturar são ações pontuais.
- Material ativo selecionável no Railway, salvo no Raspberry e aplicado às capturas automáticas e manuais.
- Catálogo inicial de fertilizantes: ureia granulada, NPK, MAP/DAP, KCl, sulfato de amônio e fertilizante orgânico.
- Peso estimado por `volume × densidade aparente`, salvo junto de cada medição.
- Confiabilidade nominal de 97% com 64/64 zonas; redução acentuada somente em caso de falha de zonas.
- Integração Raspberry ↔ Railway em validação: heartbeat, consulta de comandos e tratamento de falhas temporárias de conexão.

### Dependência bloqueadora: conectividade 4G autônoma

A integração do modem 4G **não foi concluída**. O Raspberry Pi não suportou a alimentação elétrica necessária do modem diretamente pelas portas USB. A continuação depende de um **hub USB com alimentação externa por fonte própria**.

Enquanto o hub não estiver disponível, a BoxNode permanece operando pela rede local/Wi‑Fi disponível. A arquitetura de sincronização e recuperação de conexão já está preparada para o uso futuro do modem 4G.

## Próximos critérios de aceite

1. Confirmar heartbeat estável no Railway por pelo menos 30 minutos.
2. Confirmar que a seleção de fertilizante persiste no Raspberry e atualiza o peso nas leituras automáticas.
3. Validar alerta de capacidade e envio de e-mail com uma leitura acima do limite configurado.
4. Instalar o hub USB alimentado, conectar o modem 4G e repetir os testes de sincronização sem Wi‑Fi local.
5. Registrar o segundo BoxNode para validar o fluxo multi-BoxNode.
