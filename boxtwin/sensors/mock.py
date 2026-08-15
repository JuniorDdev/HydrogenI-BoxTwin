import math
import random

from .base import DepthSensor


class MockSensor(DepthSensor):
    """Sensor virtual 8x8 para demonstrar o MVP sem hardware físico."""

    SCENARIOS = {
        "empty": {"label": "Box vazio", "description": "Linha de base para calibração."},
        "flat_25": {"label": "Carga uniforme 25%", "description": "Superfície plana em baixa ocupação."},
        "flat_50": {"label": "Carga uniforme 50%", "description": "Meia capacidade com superfície plana."},
        "flat_75": {"label": "Carga uniforme 75%", "description": "Carga elevada e distribuída."},
        "full": {"label": "Box quase cheio", "description": "Ocupação próxima do limite configurado."},
        "pile": {"label": "Pilha central", "description": "Monte de fertilizante com pico no centro."},
        "slope": {"label": "Superfície inclinada", "description": "Carga acumulada em uma das laterais."},
        "irregular": {"label": "Carga irregular", "description": "Ondulações e distribuição não uniforme."},
        "obstruction": {"label": "Sensor parcialmente obstruído", "description": "Simula zonas inválidas e baixa confiança."},
    }

    def __init__(self, box_height_m):
        self.empty_distance_mm = box_height_m * 1000
        self.box_height_m = box_height_m
        self.level_percent = 0.0
        self.scenario = "empty"
        self._capture_count = 0

    def set_level(self, level_percent):
        self.level_percent = max(0.0, min(float(level_percent), 100.0))
        self.scenario = "custom"

    def set_scenario(self, scenario):
        if scenario not in self.SCENARIOS:
            raise ValueError(f"Cenário desconhecido: {scenario}")
        self.scenario = scenario
        presets = {"empty": 0, "flat_25": 25, "flat_50": 50, "flat_75": 75, "full": 92}
        self.level_percent = presets.get(scenario, 0)

    def list_scenarios(self):
        return [{"id": key, **value} for key, value in self.SCENARIOS.items()]

    def _height_ratio(self, row, col):
        if self.scenario in {"empty", "flat_25", "flat_50", "flat_75", "full", "custom"}:
            return self.level_percent / 100

        x = (col - 3.5) / 3.5
        y = (row - 3.5) / 3.5
        radius = math.sqrt(x * x + y * y)
        if self.scenario in {"pile", "obstruction"}:
            return max(0.08, 0.86 * (1 - radius / 1.42))
        if self.scenario == "slope":
            return 0.18 + 0.62 * ((col + row) / 14)
        if self.scenario == "irregular":
            wave = 0.48 + 0.16 * math.sin(col * 1.35) + 0.12 * math.cos(row * 1.7)
            bump = 0.20 * math.exp(-((x + 0.35) ** 2 + (y - 0.2) ** 2) / 0.22)
            return max(0.08, min(wave + bump, 0.88))
        return 0.0

    @property
    def reference_percent(self):
        ratios = [self._height_ratio(row, col) for row in range(8) for col in range(8)]
        return round(sum(ratios) / 64 * 100, 1)

    def read_distance_grid_mm(self):
        self._capture_count += 1
        rng = random.Random(f"{self.scenario}-{self._capture_count}")
        grid = []
        for row in range(8):
            line = []
            for col in range(8):
                if self.scenario == "obstruction" and (
                    (row < 4 and col >= 4) or (row in {4, 5} and col >= 6)
                ):
                    line.append(None)
                    continue
                height_mm = self.empty_distance_mm * self._height_ratio(row, col)
                noise = 0 if self.scenario == "empty" else rng.uniform(-1.8, 1.8)
                line.append(round(max(0, self.empty_distance_mm - height_mm + noise), 2))
            grid.append(line)
        return grid
