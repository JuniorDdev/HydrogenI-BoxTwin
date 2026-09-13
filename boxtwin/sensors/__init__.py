from .mock import MockSensor
from .vl53l5cx import VL53L5CXSensor
from .vl53l8cx import VL53L8CXSensor


def build_sensor(mode, box_height_m, config=None):
    if mode == "mock":
        return MockSensor(box_height_m)
    if mode == "vl53l5cx":
        return VL53L5CXSensor()
    if mode == "vl53l8cx":
        config = config or {}
        return VL53L8CXSensor(
            config.get("VL53L8CX_MENU_PATH", ""),
            config.get("VL53L8CX_TIMEOUT_SECONDS", 30),
        )
    raise ValueError(f"SENSOR_MODE desconhecido: {mode}")
