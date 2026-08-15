from abc import ABC, abstractmethod


class DepthSensor(ABC):
    @abstractmethod
    def read_distance_grid_mm(self):
        """Retorna uma lista 8×8 de distâncias em milímetros; use None para zona inválida."""

