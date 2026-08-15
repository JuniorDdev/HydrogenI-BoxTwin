import os
from pathlib import Path

from dotenv import load_dotenv


def _bool(name, default=False):
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def load_config():
    load_dotenv()
    root = Path(__file__).resolve().parent.parent
    return {
        "APP_HOST": os.getenv("APP_HOST", "0.0.0.0"),
        "APP_PORT": int(os.getenv("APP_PORT", "5000")),
        "APP_DEBUG": _bool("APP_DEBUG"),
        "SENSOR_MODE": os.getenv("SENSOR_MODE", "mock"),
        "BOX_NODE_ID": os.getenv("BOX_NODE_ID", "BOX-DEMO-01"),
        "BOX_NAME": os.getenv("BOX_NAME", "Box reduzido HydrogenI"),
        "BOX_LENGTH_M": float(os.getenv("BOX_LENGTH_M", "0.60")),
        "BOX_WIDTH_M": float(os.getenv("BOX_WIDTH_M", "0.40")),
        "BOX_HEIGHT_M": float(os.getenv("BOX_HEIGHT_M", "0.50")),
        "SAMPLE_INTERVAL_SECONDS": float(os.getenv("SAMPLE_INTERVAL_SECONDS", "5")),
        "CAPACITY_ALERT_PERCENT": float(os.getenv("CAPACITY_ALERT_PERCENT", "85")),
        "MIN_CONFIDENCE_PERCENT": float(os.getenv("MIN_CONFIDENCE_PERCENT", "70")),
        "DATABASE_PATH": str(root / os.getenv("DATABASE_PATH", "data/boxtwin.db")),
        "CALIBRATION_PATH": str(root / os.getenv("CALIBRATION_PATH", "data/calibration.json")),
    }

