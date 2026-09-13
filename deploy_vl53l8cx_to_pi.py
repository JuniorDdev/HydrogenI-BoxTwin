"""Install the VL53L8CX adapter into an existing BoxTwin checkout on Raspberry Pi."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent
TARGET_ROOT = Path(sys.argv[1]).expanduser() if len(sys.argv) == 2 else Path.home() / "HydrogenI-BoxTwin"


def backup(path: Path) -> None:
    backup_path = path.with_name(f"{path.name}.bak-vl53l8cx")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    if new in content:
        return
    if old not in content:
        raise RuntimeError(f"Nao encontrei o trecho esperado em {path}.")
    backup(path)
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    if not (TARGET_ROOT / "boxtwin" / "runtime.py").is_file():
        raise RuntimeError(f"BoxTwin nao encontrado em {TARGET_ROOT}.")

    sensor_target = TARGET_ROOT / "boxtwin" / "sensors" / "vl53l8cx.py"
    backup(sensor_target)
    shutil.copy2(SOURCE_ROOT / "boxtwin" / "sensors" / "vl53l8cx.py", sensor_target)

    replace_once(
        TARGET_ROOT / "boxtwin" / "sensors" / "__init__.py",
        "def build_sensor(mode, box_height_m):",
        "def build_sensor(mode, box_height_m, config=None):",
    )
    replace_once(
        TARGET_ROOT / "boxtwin" / "sensors" / "__init__.py",
        'return VL53L8CXSensor()',
        'config = config or {}\n        return VL53L8CXSensor(\n'
        '            config.get("VL53L8CX_MENU_PATH", ""),\n'
        '            config.get("VL53L8CX_TIMEOUT_SECONDS", 30),\n'
        '        )',
    )
    replace_once(
        TARGET_ROOT / "boxtwin" / "runtime.py",
        'build_sensor(config["SENSOR_MODE"], config["BOX_HEIGHT_M"])',
        'build_sensor(config["SENSOR_MODE"], config["BOX_HEIGHT_M"], config)',
    )
    replace_once(
        TARGET_ROOT / "boxtwin" / "config.py",
        '"SENSOR_MODE": os.getenv("SENSOR_MODE", "mock"),',
        '"SENSOR_MODE": os.getenv("SENSOR_MODE", "mock"),\n'
        '        "VL53L8CX_MENU_PATH": os.getenv("VL53L8CX_MENU_PATH", ""),\n'
        '        "VL53L8CX_TIMEOUT_SECONDS": float(os.getenv("VL53L8CX_TIMEOUT_SECONDS", "30")),',
    )
    print("Integracao instalada. Backups terminam com .bak-vl53l8cx.")


if __name__ == "__main__":
    main()
