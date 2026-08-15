from .base import DepthSensor


class VL53L8CXSensor(DepthSensor):
    """Adaptador reservado para a placa VL53L8CX física.

    O painel e o cálculo já esperam uma matriz 8x8 em milímetros. Quando a
    placa for adquirida, somente este adaptador precisará receber o driver
    indicado pelo fabricante da breakout.
    """

    def __init__(self):
        raise RuntimeError(
            "Driver do VL53L8CX ainda não configurado. Use SENSOR_MODE=mock "
            "para o Hackathon sem o hardware físico."
        )

    def read_distance_grid_mm(self):
        raise NotImplementedError
