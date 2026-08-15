import random

from .base import DepthSensor


class MockSensor(DepthSensor):
    def __init__(self, box_height_m):
        self.empty_distance_mm = box_height_m * 1000
        # Inicia vazio para que a primeira calibração represente a linha de base.
        self.level_percent = 0.0

    def set_level(self, level_percent):
        self.level_percent = max(0.0, min(float(level_percent), 100.0))

    def read_distance_grid_mm(self):
        grid = []
        normalized = self.level_percent / 100
        for row in range(8):
            line = []
            for col in range(8):
                radial = max(0.20, 1 - (((row - 3.5) ** 2 + (col - 3.5) ** 2) / 38))
                pile_height = self.empty_distance_mm * normalized * radial
                noise = random.uniform(-2.5, 2.5)
                line.append(round(self.empty_distance_mm - pile_height + noise, 2))
            grid.append(line)
        return grid
