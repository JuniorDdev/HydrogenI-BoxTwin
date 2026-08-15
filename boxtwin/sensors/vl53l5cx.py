from .base import DepthSensor


class VL53L5CXSensor(DepthSensor):
    """Ponto de integração com o driver físico da placa breakout adquirida."""

    def __init__(self):
        raise RuntimeError(
            "Driver físico ainda não configurado. Use SENSOR_MODE=mock até instalar "
            "o pacote indicado pelo fabricante da placa VL53L5CX."
        )

    def read_distance_grid_mm(self):
        raise NotImplementedError

