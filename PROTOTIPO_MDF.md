# Prototipo MDF - BoxTwin 3D

## Dimensoes recomendadas

Para melhor precisao com sensor ToF 8 x 8, use um box quadrado menor:

```text
Area interna: 40 cm x 40 cm
Altura interna util: 40 cm
Capacidade geometrica: 64 litros
Altura maxima recomendada de carga nos testes: 30 cm
Capacidade operacional de teste: 48 litros
Sensor: centralizado sobre o box, apontando para baixo
Altura sugerida do sensor ate o fundo interno: 70 a 80 cm
Distancia minima sensor-carga cheia: 40 a 50 cm
```

## Por que 40 x 40 cm

O sensor 8 x 8 divide a base em 64 zonas. Com base de 40 x 40 cm, cada zona representa
aproximadamente 5 x 5 cm. Isso melhora a leitura de pilhas, bordas e irregularidades em comparacao
com uma base de 60 x 40 cm.

## Variaveis do sistema

Use estas dimensoes no Railway e no Raspberry:

```env
BOX_LENGTH_M=0.40
BOX_WIDTH_M=0.40
BOX_HEIGHT_M=0.40
```

Depois de alterar as medidas, sempre calibre o box vazio antes dos testes.

## Volumes para validacao

Com capacidade geometrica de 64 litros:

```text
16 litros = 25%
32 litros = 50%
48 litros = 75%
64 litros = 100%
```

Para operar com limite seguro de 30 cm de material:

```text
12 litros = 18,75%
24 litros = 37,50%
36 litros = 56,25%
48 litros = 75,00%
```

## Lista de corte para MDF 10 mm

Assumindo MDF de 10 mm e dimensoes internas de 40 x 40 x 40 cm:

```text
1 base: 42 cm x 42 cm
2 laterais: 42 cm x 40 cm
2 laterais: 40 cm x 40 cm
```

Com essa montagem, as paredes ficam ao redor da base e o vao interno fica proximo de 40 x 40 cm.

## Lista de corte para MDF 15 mm

Assumindo MDF de 15 mm e mantendo o mesmo vao interno:

```text
1 base: 43 cm x 43 cm
2 laterais: 43 cm x 40 cm
2 laterais: 40 cm x 40 cm
```

Em qualquer espessura, confirme com quem vai montar que a medida interna final precisa ficar em
40 cm x 40 cm, pois e essa dimensao que o software usa para calcular o volume.

## Estrutura do sensor

```text
Altura total da haste: 70 a 80 cm acima do fundo interno
Sensor centralizado: 20 cm da lateral esquerda e 20 cm da lateral frontal
Fixacao: rigida, sem vibracao
Orientacao: sensor apontado perpendicularmente para o fundo do box
```

## Materiais de teste

Use material seguro e granular:

```text
milho
arroz com casca
serragem granulada
pellets
```

Evite fertilizante real na demonstracao inicial por seguranca, poeira e corrosao.
