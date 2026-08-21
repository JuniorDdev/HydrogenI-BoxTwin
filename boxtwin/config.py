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
        "BOX_NAME": os.getenv("BOX_NAME", "BoxTwin 3D - prototipo MDF 40x40"),
        "BOX_LENGTH_M": float(os.getenv("BOX_LENGTH_M", "0.40")),
        "BOX_WIDTH_M": float(os.getenv("BOX_WIDTH_M", "0.40")),
        "BOX_HEIGHT_M": float(os.getenv("BOX_HEIGHT_M", "0.40")),
        "SAMPLE_INTERVAL_SECONDS": float(os.getenv("SAMPLE_INTERVAL_SECONDS", "5")),
        "CAPACITY_ALERT_PERCENT": float(os.getenv("CAPACITY_ALERT_PERCENT", "85")),
        "MIN_CONFIDENCE_PERCENT": float(os.getenv("MIN_CONFIDENCE_PERCENT", "70")),
        "SECRET_KEY": os.getenv("SECRET_KEY", "troque-esta-chave-no-ambiente"),
        "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME", "admin"),
        "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD", "HydrogenI@2026"),
        "NOTIFY_COOLDOWN_SECONDS": int(os.getenv("NOTIFY_COOLDOWN_SECONDS", "300")),
        "EMAIL_ENABLED": _bool("EMAIL_ENABLED"),
        "RESEND_API_KEY": os.getenv("RESEND_API_KEY", ""),
        "RESEND_FROM_EMAIL": os.getenv("RESEND_FROM_EMAIL", ""),
        "ALERT_EMAIL_TO": os.getenv("ALERT_EMAIL_TO", ""),
        "TWILIO_ENABLED": _bool("TWILIO_ENABLED"),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "TWILIO_FROM": os.getenv("TWILIO_FROM", ""),
        "TWILIO_TO": os.getenv("TWILIO_TO", ""),
        "TWILIO_CONTENT_SID": os.getenv("TWILIO_CONTENT_SID", ""),
        "PUBLIC_BASE_URL": os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:5000").rstrip("/"),
        "GROQ_ENABLED": _bool("GROQ_ENABLED"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
        "GROQ_MODEL": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "GROQ_TIMEOUT_SECONDS": int(os.getenv("GROQ_TIMEOUT_SECONDS", "20")),
        "TWILIO_VALIDATE_SIGNATURE": _bool("TWILIO_VALIDATE_SIGNATURE", True),
        "EDGE_SYNC_ENABLED": _bool("EDGE_SYNC_ENABLED"),
        "EDGE_SYNC_TARGET_URL": os.getenv("EDGE_SYNC_TARGET_URL", "").rstrip("/"),
        "EDGE_SYNC_TOKEN": os.getenv("EDGE_SYNC_TOKEN", ""),
        "EDGE_SYNC_TIMEOUT_SECONDS": int(os.getenv("EDGE_SYNC_TIMEOUT_SECONDS", "15")),
        "EDGE_SYNC_BATCH_SIZE": int(os.getenv("EDGE_SYNC_BATCH_SIZE", "20")),
        "AUTO_CLEANUP_ENABLED": _bool("AUTO_CLEANUP_ENABLED", True),
        "READINGS_RETENTION_DAYS": int(os.getenv("READINGS_RETENTION_DAYS", "45")),
        "NOTIFICATIONS_RETENTION_DAYS": int(os.getenv("NOTIFICATIONS_RETENTION_DAYS", "60")),
        "INCIDENTS_RETENTION_DAYS": int(os.getenv("INCIDENTS_RETENTION_DAYS", "180")),
        "SYNC_QUEUE_RETENTION_DAYS": int(os.getenv("SYNC_QUEUE_RETENTION_DAYS", "7")),
        "DATABASE_PATH": str(root / os.getenv("DATABASE_PATH", "data/boxtwin.db")),
        "CALIBRATION_PATH": str(root / os.getenv("CALIBRATION_PATH", "data/calibration.json")),
    }
