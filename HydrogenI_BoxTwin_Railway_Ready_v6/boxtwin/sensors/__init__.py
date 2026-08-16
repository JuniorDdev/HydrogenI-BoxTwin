from .mock import MockSensor
from .vl53l5cx import VL53L5CXSensor
from .vl53l8cx import VL53L8CXSensor


def build_sensor(mode, box_height_m):
    if mode == "mock":
        return MockSensor(box_height_m)
    if mode == "vl53l5cx":
        return VL53L5CXSensor()
    if mode == "vl53l8cx":
        return VL53L8CXSensor()
    raise ValueError(f"SENSOR_MODE desconhecido: {mode}")
