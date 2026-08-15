import json
import sqlite3
from datetime import datetime, timezone


class Database:
    def __init__(self, path):
        self.path = path

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    volume_m3 REAL NOT NULL,
                    capacity_percent REAL NOT NULL,
                    confidence_percent REAL NOT NULL,
                    valid_zones INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    alerts_json TEXT NOT NULL,
                    grid_json TEXT NOT NULL
                )
            """)

    def save_reading(self, reading):
        created_at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute("""
                INSERT INTO readings (
                    created_at, node_id, volume_m3, capacity_percent,
                    confidence_percent, valid_zones, status, alerts_json, grid_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                created_at, reading["node_id"], reading["volume_m3"], reading["capacity_percent"],
                reading["confidence_percent"], reading["valid_zones"], reading["status"],
                json.dumps(reading["alerts"]), json.dumps(reading["height_grid_m"]),
            ))
            return cursor.lastrowid, created_at

    def latest(self):
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1").fetchone()
        return self._serialize(row) if row else None

    def history(self, limit=50):
        limit = max(1, min(int(limit), 500))
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [self._serialize(row) for row in reversed(rows)]

    @staticmethod
    def _serialize(row):
        return {
            "id": row["id"], "created_at": row["created_at"], "node_id": row["node_id"],
            "volume_m3": row["volume_m3"], "capacity_percent": row["capacity_percent"],
            "confidence_percent": row["confidence_percent"], "valid_zones": row["valid_zones"],
            "status": row["status"], "alerts": json.loads(row["alerts_json"]),
            "height_grid_m": json.loads(row["grid_json"]),
        }

