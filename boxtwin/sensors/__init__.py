from .mock import MockSensor
from .vl53l5cx import VL53L5CXSensor


def build_sensor(mode, box_height_m):
    if mode == "mock":
        return MockSensor(box_height_m)
    if mode == "vl53l5cx":
        return VL53L5CXSensor()
    raise ValueError(f"SENSOR_MODE desconhecido: {mode}")

