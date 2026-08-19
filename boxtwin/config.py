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
        "APP_PORT": int(os.getenv("PORT", os.getenv("APP_PORT", "5000"))),
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
        "SECRET_KEY": os.getenv("SECRET_KEY", "troque-esta-chave-no-ambiente"),
        "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME", "admin"),
        "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD", "HydrogenI@2026"),
        "NOTIFY_COOLDOWN_SECONDS": int(os.getenv("NOTIFY_COOLDOWN_SECONDS", "300")),
        "EMAIL_ENABLED": _bool("EMAIL_ENABLED"),
        "SMTP_HOST": os.getenv("SMTP_HOST", ""),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME", ""),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
        "ALERT_EMAIL_TO": os.getenv("ALERT_EMAIL_TO", ""),
        "TWILIO_ENABLED": _bool("TWILIO_ENABLED"),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "TWILIO_FROM": os.getenv("TWILIO_FROM", ""),
        "TWILIO_TO": os.getenv("TWILIO_TO", ""),
        "PUBLIC_BASE_URL": os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:5000").rstrip("/"),
        "XAI_ENABLED": _bool("XAI_ENABLED"),
        "XAI_API_KEY": os.getenv("XAI_API_KEY", ""),
        "XAI_MODEL": os.getenv("XAI_MODEL", "latest"),
        "XAI_BASE_URL": os.getenv("XAI_BASE_URL", "https://api.x.ai/v1").rstrip("/"),
        "XAI_TIMEOUT_SECONDS": int(os.getenv("XAI_TIMEOUT_SECONDS", "20")),
        "TWILIO_VALIDATE_SIGNATURE": _bool("TWILIO_VALIDATE_SIGNATURE", True),
        "DATABASE_PATH": str(root / os.getenv("DATABASE_PATH", "data/boxtwin.db")),
        "CALIBRATION_PATH": str(root / os.getenv("CALIBRATION_PATH", "data/calibration.json")),
        "SSL_CERT_PATH": os.getenv("SSL_CERT_PATH", ""),
        "SSL_KEY_PATH": os.getenv("SSL_KEY_PATH", ""),
        "SSL_AUTO_GENERATE": _bool("SSL_AUTO_GENERATE", False),
        "OFFLINE_QUEUE_PATH": str(root / os.getenv("OFFLINE_QUEUE_PATH", "data/offline_queue.json")),
    }
