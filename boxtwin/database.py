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
                    grid_json TEXT NOT NULL,
                    scenario TEXT,
                    reference_percent REAL,
                    reference_error_points REAL,
                    average_height_m REAL,
                    maximum_height_m REAL,
                    capacity_m3 REAL
                )
            """)
            existing = {row[1] for row in connection.execute("PRAGMA table_info(readings)")}
            migrations = {
                "scenario": "TEXT",
                "reference_percent": "REAL",
                "reference_error_points": "REAL",
                "average_height_m": "REAL",
                "maximum_height_m": "REAL",
                "capacity_m3": "REAL",
            }
            for column, column_type in migrations.items():
                if column not in existing:
                    connection.execute(f"ALTER TABLE readings ADD COLUMN {column} {column_type}")
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    reading_id INTEGER,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    acknowledged_at TEXT,
                    resolution_note TEXT
                );
                CREATE TABLE IF NOT EXISTS notification_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    anomaly_id INTEGER,
                    channel TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT,
                    provider_message_id TEXT,
                    delivery_status TEXT,
                    recipient_id INTEGER
                );
                CREATE TABLE IF NOT EXISTS recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    recipient_type TEXT NOT NULL DEFAULT 'administrator',
                    team_name TEXT,
                    email TEXT,
                    phone TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS notification_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL DEFAULT '*',
                    recipient_id INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    escalation_minutes INTEGER NOT NULL DEFAULT 0,
                    active INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY(recipient_id) REFERENCES recipients(id)
                );
                CREATE TABLE IF NOT EXISTS incident_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anomaly_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    note TEXT
                );
            """)
            notification_columns = {row[1] for row in connection.execute("PRAGMA table_info(notification_log)")}
            for column in ("provider_message_id", "delivery_status", "recipient_id"):
                if column not in notification_columns:
                    connection.execute(f"ALTER TABLE notification_log ADD COLUMN {column} {'INTEGER' if column == 'recipient_id' else 'TEXT'}")

    def save_reading(self, reading):
        created_at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute("""
                INSERT INTO readings (
                    created_at, node_id, volume_m3, capacity_percent,
                    confidence_percent, valid_zones, status, alerts_json, grid_json
                    , scenario, reference_percent, reference_error_points,
                    average_height_m, maximum_height_m, capacity_m3
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                created_at, reading["node_id"], reading["volume_m3"], reading["capacity_percent"],
                reading["confidence_percent"], reading["valid_zones"], reading["status"],
                json.dumps(reading["alerts"]), json.dumps(reading["height_grid_m"]),
                reading.get("scenario"), reading.get("reference_percent"),
                reading.get("reference_error_points"), reading.get("average_height_m"),
                reading.get("maximum_height_m"), reading.get("capacity_m3"),
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

    def save_anomalies(self, reading_id, alerts):
        created_at = datetime.now(timezone.utc).isoformat()
        records = []
        with self.connect() as connection:
            for alert in alerts:
                cursor = connection.execute(
                    "INSERT INTO anomalies (created_at, reading_id, anomaly_type, severity, message) VALUES (?, ?, ?, ?, ?)",
                    (created_at, reading_id, alert["type"], alert["level"], alert["message"]),
                )
                records.append({"id": cursor.lastrowid, "created_at": created_at, **alert, "status": "open"})
        return records

    def anomalies(self, limit=100, status=None):
        query, params = "SELECT * FROM anomalies", []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(max(1, min(int(limit), 500)))
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(query, params).fetchall()]

    def update_anomaly_status(self, anomaly_id, status, note="", actor="Administrador"):
        allowed = {"open", "acknowledged", "in_progress", "resolved", "false_positive"}
        if status not in allowed:
            raise ValueError("Status de anomalia inválido.")
        at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute(
                "UPDATE anomalies SET status=?, acknowledged_at=COALESCE(acknowledged_at, ?), resolution_note=? WHERE id=?",
                (status, at, note, anomaly_id),
            )
            if cursor.rowcount:
                connection.execute(
                    "INSERT INTO incident_events (anomaly_id, created_at, actor, event_type, note) VALUES (?, ?, ?, ?, ?)",
                    (anomaly_id, at, actor, status, note),
                )
        return cursor.rowcount > 0

    def acknowledge_anomaly(self, anomaly_id, note=""):
        return self.update_anomaly_status(anomaly_id, "acknowledged", note)

    def anomaly_detail(self, anomaly_id):
        with self.connect() as connection:
            anomaly = connection.execute("SELECT * FROM anomalies WHERE id=?", (anomaly_id,)).fetchone()
            if not anomaly:
                return None
            reading = connection.execute("SELECT * FROM readings WHERE id=?", (anomaly["reading_id"],)).fetchone()
            events = connection.execute("SELECT * FROM incident_events WHERE anomaly_id=? ORDER BY id", (anomaly_id,)).fetchall()
            notifications = connection.execute("SELECT * FROM notification_log WHERE anomaly_id=? ORDER BY id DESC", (anomaly_id,)).fetchall()
        return {"anomaly": dict(anomaly), "reading": self._serialize(reading) if reading else None, "events": [dict(x) for x in events], "notifications": [dict(x) for x in notifications]}

    def save_recipient(self, payload):
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO recipients (name, recipient_type, team_name, email, phone, active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (payload["name"], payload.get("recipient_type", "administrator"), payload.get("team_name"), payload.get("email"), payload.get("phone"), int(payload.get("active", True)), now),
            )
            return cursor.lastrowid

    def recipients(self):
        with self.connect() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM recipients ORDER BY active DESC, name").fetchall()]

    def save_rule(self, payload):
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO notification_rules (anomaly_type, severity, recipient_id, channel, escalation_minutes, active) VALUES (?, ?, ?, ?, ?, ?)",
                (payload["anomaly_type"], payload.get("severity", "*"), int(payload["recipient_id"]), payload["channel"], max(0, int(payload.get("escalation_minutes", 0))), int(payload.get("active", True))),
            )
            return cursor.lastrowid

    def rules(self):
        with self.connect() as connection:
            rows = connection.execute("SELECT r.*, p.name recipient_name, p.email, p.phone FROM notification_rules r JOIN recipients p ON p.id=r.recipient_id ORDER BY r.id DESC").fetchall()
        return [dict(row) for row in rows]

    def matching_rules(self, anomaly):
        with self.connect() as connection:
            rows = connection.execute("""SELECT r.*, p.name recipient_name, p.email, p.phone
                FROM notification_rules r JOIN recipients p ON p.id=r.recipient_id
                WHERE r.active=1 AND p.active=1 AND (r.anomaly_type=? OR r.anomaly_type='*')
                AND (r.severity=? OR r.severity='*') ORDER BY r.escalation_minutes""",
                (anomaly["type"], anomaly["level"])).fetchall()
        return [dict(row) for row in rows]

    def due_escalations(self):
        now = datetime.now(timezone.utc)
        due = []
        with self.connect() as connection:
            anomalies = connection.execute("SELECT * FROM anomalies WHERE status IN ('open','acknowledged','in_progress')").fetchall()
            for row in anomalies:
                anomaly = dict(row)
                age_minutes = (now - datetime.fromisoformat(anomaly["created_at"])).total_seconds() / 60
                rules = connection.execute("""SELECT r.*, p.name recipient_name, p.email, p.phone
                    FROM notification_rules r JOIN recipients p ON p.id=r.recipient_id
                    WHERE r.active=1 AND p.active=1 AND r.escalation_minutes>0
                    AND (r.anomaly_type=? OR r.anomaly_type='*') AND (r.severity=? OR r.severity='*')""",
                    (anomaly["anomaly_type"], anomaly["severity"])).fetchall()
                for rule_row in rules:
                    rule = dict(rule_row)
                    already = connection.execute("SELECT 1 FROM notification_log WHERE anomaly_id=? AND recipient_id=? AND channel=?", (anomaly["id"], rule["recipient_id"], rule["channel"])).fetchone()
                    if age_minutes >= rule["escalation_minutes"] and not already:
                        due.append(({"id": anomaly["id"], "type": anomaly["anomaly_type"], "level": anomaly["severity"], "message": anomaly["message"], "created_at": anomaly["created_at"]}, rule))
        return due

    def log_notification(self, anomaly_id, channel, status, detail="", provider_message_id=None, recipient_id=None):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO notification_log (created_at, anomaly_id, channel, status, detail, provider_message_id, delivery_status, recipient_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), anomaly_id, channel, status, detail, provider_message_id, status, recipient_id),
            )

    def update_delivery_status(self, provider_message_id, status, detail=""):
        with self.connect() as connection:
            cursor = connection.execute("UPDATE notification_log SET delivery_status=?, detail=COALESCE(NULLIF(?,''), detail) WHERE provider_message_id=?", (status, detail, provider_message_id))
        return cursor.rowcount

    def notification_history(self, limit=100):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM notification_log ORDER BY id DESC LIMIT ?", (max(1, min(int(limit), 500)),)
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _serialize(row):
        return {
            "id": row["id"], "created_at": row["created_at"], "node_id": row["node_id"],
            "volume_m3": row["volume_m3"], "capacity_percent": row["capacity_percent"],
            "confidence_percent": row["confidence_percent"], "valid_zones": row["valid_zones"],
            "status": row["status"], "alerts": json.loads(row["alerts_json"]),
            "height_grid_m": json.loads(row["grid_json"]),
            "scenario": row["scenario"], "reference_percent": row["reference_percent"],
            "reference_error_points": row["reference_error_points"],
            "average_height_m": row["average_height_m"],
            "maximum_height_m": row["maximum_height_m"], "capacity_m3": row["capacity_m3"],
        }
