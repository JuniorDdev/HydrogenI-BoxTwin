# Roteiro rápido de demonstração — HydrogenI BoxTwin 3D

## Preparação

1. Execute `python app.py`, apresente `http://127.0.0.1:5000` e abra o simulador pelo botão principal ou por `http://127.0.0.1:5000/simulador`.
2. Clique em **Preparar demonstração**.
3. Deixe aberta a visualização da pilha central.
4. Teste previamente os cenários 50%, irregular, quase cheio e obstrução.

## Demonstração sugerida

1. **Problema:** explique que o estoque atual depende de estimativa visual e atualização manual.
2. **Box vazio:** selecione o cenário vazio e mostre a calibração da referência.
3. **Medição conhecida:** selecione 50% e destaque volume, ocupação e erro contra a referência.
4. **Carga realista:** selecione pilha central ou irregular e mostre por que uma medição em ponto único não representa toda a superfície.
5. **Alerta:** selecione quase cheio e mostre o alerta de capacidade.
6. **Confiabilidade:** selecione obstrução e mostre a redução das zonas válidas.
7. **Evolução:** informe que o sensor virtual será substituído pelo VL53L8CX sem alterar cálculo, banco ou painel.
8. **Operação:** entre em `/admin`, mostre o assistente técnico, a fila de incidentes e baixe o relatório PDF.

## Frase de encerramento

“Hoje demonstramos todo o fluxo de decisão com uma matriz virtual 8×8. Com o VL53L8CX, substituímos apenas a origem dos dados e mantemos o mesmo cálculo volumétrico, histórico, alertas e gêmeo digital.”
