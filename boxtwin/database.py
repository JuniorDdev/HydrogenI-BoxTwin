import json
import sqlite3
from datetime import datetime, timedelta, timezone


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
                    reading_uuid TEXT UNIQUE,
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
                "reading_uuid": "TEXT",
                "scenario": "TEXT",
                "reference_percent": "REAL",
                "reference_error_points": "REAL",
                "average_height_m": "REAL",
                "maximum_height_m": "REAL",
                "capacity_m3": "REAL",
                "box_id": "TEXT",
                "sensor_id": "TEXT",
                "material_type": "TEXT",
                "material_name": "TEXT",
                "density_t_m3": "REAL",
                "expected_volume_m3": "REAL",
                "estimated_tons": "REAL",
                "reading_duration_ms": "INTEGER",
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
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reading_id INTEGER NOT NULL UNIQUE,
                    reading_uuid TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    target_url TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_attempt_at TEXT,
                    synced_at TEXT,
                    last_error TEXT,
                    FOREIGN KEY(reading_id) REFERENCES readings(id)
                );
                CREATE TABLE IF NOT EXISTS live_sensor_grids (
                    node_id TEXT PRIMARY KEY,
                    captured_at TEXT NOT NULL,
                    valid_zones INTEGER NOT NULL,
                    distance_grid_json TEXT NOT NULL,
                    received_at TEXT NOT NULL
                );
            """)
            notification_columns = {row[1] for row in connection.execute("PRAGMA table_info(notification_log)")}
            for column in ("provider_message_id", "delivery_status", "recipient_id"):
                if column not in notification_columns:
                    connection.execute(f"ALTER TABLE notification_log ADD COLUMN {column} {'INTEGER' if column == 'recipient_id' else 'TEXT'}")
            connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_readings_uuid ON readings(reading_uuid)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status, id)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_readings_created_at ON readings(created_at)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_readings_box_material ON readings(box_id, material_type)")

    def upsert_live_sensor_grid(self, payload):
        """Keep the most recent uncalibrated 8x8 frame for each BoxNode."""
        received_at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO live_sensor_grids
                    (node_id, captured_at, valid_zones, distance_grid_json, received_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    captured_at=excluded.captured_at,
                    valid_zones=excluded.valid_zones,
                    distance_grid_json=excluded.distance_grid_json,
                    received_at=excluded.received_at
                """,
                (
                    payload["node_id"], payload["captured_at"], int(payload["valid_zones"]),
                    json.dumps(payload["distance_grid_mm"], ensure_ascii=False), received_at,
                ),
            )
        return self.latest_live_sensor_grid(payload["node_id"])

    def latest_live_sensor_grid(self, node_id=None):
        with self.connect() as connection:
            if node_id:
                row = connection.execute(
                    "SELECT * FROM live_sensor_grids WHERE node_id=?", (node_id,)
                ).fetchone()
            else:
                row = connection.execute(
                    "SELECT * FROM live_sensor_grids ORDER BY received_at DESC LIMIT 1"
                ).fetchone()
        if not row:
            return None
        return {
            "node_id": row["node_id"], "captured_at": row["captured_at"],
            "received_at": row["received_at"], "valid_zones": row["valid_zones"],
            "distance_grid_mm": json.loads(row["distance_grid_json"]),
        }

    def save_reading(self, reading):
        created_at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute("""
                INSERT INTO readings (
                    reading_uuid, created_at, node_id, volume_m3, capacity_percent,
                    confidence_percent, valid_zones, status, alerts_json, grid_json
                    , scenario, reference_percent, reference_error_points,
                    average_height_m, maximum_height_m, capacity_m3, box_id, sensor_id,
                    material_type, material_name, density_t_m3, expected_volume_m3,
                    estimated_tons, reading_duration_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                reading["reading_uuid"], created_at, reading["node_id"], reading["volume_m3"], reading["capacity_percent"],
                reading["confidence_percent"], reading["valid_zones"], reading["status"],
                json.dumps(reading["alerts"]), json.dumps(reading["height_grid_m"]),
                reading.get("scenario"), reading.get("reference_percent"),
                reading.get("reference_error_points"), reading.get("average_height_m"),
                reading.get("maximum_height_m"), reading.get("capacity_m3"),
                reading.get("box_id") or reading["node_id"], reading.get("sensor_id") or reading["node_id"],
                reading.get("material_type") or "nao_informado", reading.get("material_name") or "Não informado",
                reading.get("density_t_m3"), reading.get("expected_volume_m3"),
                reading.get("estimated_tons"), reading.get("reading_duration_ms"),
            ))
            return cursor.lastrowid, created_at

    def find_reading_by_uuid(self, reading_uuid):
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM readings WHERE reading_uuid=?", (reading_uuid,)).fetchone()
        return self._serialize(row) if row else None

    def enqueue_sync(self, reading_id, reading_uuid, payload, target_url):
        with self.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO sync_queue
                (reading_id, reading_uuid, created_at, payload_json, target_url, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
                """,
                (
                    reading_id,
                    reading_uuid,
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(payload, ensure_ascii=False),
                    target_url,
                ),
            )

    def sync_queue_batch(self, limit=20):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM sync_queue
                WHERE status IN ('pending', 'failed')
                ORDER BY id
                LIMIT ?
                """,
                (max(1, min(int(limit), 100)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_sync_attempt(self, item_id):
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE sync_queue
                SET attempts = attempts + 1,
                    last_attempt_at = ?,
                    status = 'retrying'
                WHERE id=?
                """,
                (datetime.now(timezone.utc).isoformat(), item_id),
            )

    def mark_sync_success(self, item_id):
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            connection.execute(
                "UPDATE sync_queue SET status='synced', synced_at=?, last_error=NULL WHERE id=?",
                (now, item_id),
            )

    def mark_sync_failure(self, item_id, error_message):
        with self.connect() as connection:
            connection.execute(
                "UPDATE sync_queue SET status='failed', last_error=? WHERE id=?",
                (str(error_message)[:500], item_id),
            )

    def sync_status(self):
        with self.connect() as connection:
            counts = {
                row["status"]: row["count"]
                for row in connection.execute(
                    "SELECT status, COUNT(*) count FROM sync_queue GROUP BY status"
                ).fetchall()
            }
            latest = connection.execute(
                "SELECT synced_at, last_attempt_at, last_error, target_url FROM sync_queue ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return {
            "pending": counts.get("pending", 0),
            "retrying": counts.get("retrying", 0),
            "failed": counts.get("failed", 0),
            "synced": counts.get("synced", 0),
            "last_synced_at": latest["synced_at"] if latest else None,
            "last_attempt_at": latest["last_attempt_at"] if latest else None,
            "last_error": latest["last_error"] if latest else None,
            "target_url": latest["target_url"] if latest else None,
        }

    def ingest_synced_reading(self, reading):
        existing = self.find_reading_by_uuid(reading["reading_uuid"])
        if existing:
            return existing["id"], existing["created_at"], False
        return (*self.save_reading(reading), True)

    def latest(self):
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1").fetchone()
        return self._serialize(row) if row else None

    def history(self, limit=50):
        limit = max(1, min(int(limit), 500))
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [self._serialize(row) for row in reversed(rows)]

    def analytics(self, filters=None):
        """Return manager KPIs while keeping legacy readings usable."""
        filters = filters or {}
        clauses, params = [], []
        for key, column in (("sensor_id", "sensor_id"), ("box_id", "box_id"), ("material_type", "material_type")):
            value = (filters.get(key) or "").strip()
            if value:
                clauses.append(f"COALESCE({column}, node_id)=?")
                params.append(value)
        start, end = (filters.get("start") or "").strip(), (filters.get("end") or "").strip()
        if start:
            clauses.append("created_at >= ?")
            params.append(start)
        if end:
            clauses.append("created_at <= ?")
            params.append(end + "T23:59:59.999999+00:00" if len(end) == 10 else end)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self.connect() as connection:
            rows = connection.execute(f"SELECT * FROM readings{where} ORDER BY created_at", params).fetchall()
            options = {
                "sensors": [row[0] for row in connection.execute("SELECT DISTINCT COALESCE(sensor_id,node_id) FROM readings ORDER BY 1")],
                "boxes": [row[0] for row in connection.execute("SELECT DISTINCT COALESCE(box_id,node_id) FROM readings ORDER BY 1")],
                "materials": [row[0] for row in connection.execute("SELECT DISTINCT COALESCE(material_type,'nao_informado') FROM readings ORDER BY 1")],
            }
        items = [self._serialize(row) for row in rows]
        volumes = [item["volume_m3"] for item in items]
        durations = [item["reading_duration_ms"] for item in items if item["reading_duration_ms"] is not None]
        tons = [item["estimated_tons"] for item in items if item["estimated_tons"] is not None]
        expected = [item for item in items if item["expected_volume_m3"] not in (None, 0)]
        deviations = [((item["volume_m3"] - item["expected_volume_m3"]) / item["expected_volume_m3"] * 100) for item in expected]
        by_day = {}
        for item in items:
            key = item["created_at"][:10]
            bucket = by_day.setdefault(key, {"date": key, "readings": 0, "volume_m3": 0.0, "estimated_tons": 0.0})
            bucket["readings"] += 1
            bucket["volume_m3"] += item["volume_m3"]
            bucket["estimated_tons"] += item["estimated_tons"] or 0
        return {
            "filters": options,
            "items": items,
            "kpis": {
                "readings_count": len(items), "unique_boxes": len({item["box_id"] for item in items}),
                "total_volume_m3": round(sum(volumes), 5), "average_volume_m3": round(sum(volumes) / len(volumes), 5) if volumes else 0,
                "estimated_tons": round(sum(tons), 4), "average_reading_ms": round(sum(durations) / len(durations), 1) if durations else None,
                "above_expected_count": sum(value > 10 for value in deviations), "below_expected_count": sum(value < -10 for value in deviations),
                "average_deviation_percent": round(sum(deviations) / len(deviations), 2) if deviations else None,
                "forecast_next_period_m3": round((sum(volumes) / len(volumes)) * min(30, max(1, len(by_day))), 5) if volumes else 0,
            },
            "series": list(by_day.values()),
        }

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
            if status == "active":
                query += " WHERE status IN ('open', 'acknowledged', 'in_progress')"
            elif status == "closed":
                query += " WHERE status IN ('resolved', 'false_positive')"
            else:
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
            values = (
                payload["anomaly_type"], payload.get("severity", "*"),
                int(payload["recipient_id"]), payload["channel"],
                max(0, int(payload.get("escalation_minutes", 0))),
            )
            existing = connection.execute(
                """SELECT id FROM notification_rules
                   WHERE anomaly_type=? AND severity=? AND recipient_id=?
                     AND channel=? AND escalation_minutes=? AND active=1
                   ORDER BY id LIMIT 1""",
                values,
            ).fetchone()
            if existing:
                return existing["id"]
            cursor = connection.execute(
                "INSERT INTO notification_rules (anomaly_type, severity, recipient_id, channel, escalation_minutes, active) VALUES (?, ?, ?, ?, ?, ?)",
                (*values, int(payload.get("active", True))),
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

    def active_alerts(self, limit=10):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    a.id,
                    a.created_at,
                    a.anomaly_type,
                    a.severity,
                    a.message,
                    a.status,
                    a.acknowledged_at,
                    EXISTS(
                        SELECT 1
                        FROM notification_log n
                        WHERE n.anomaly_id = a.id
                          AND n.channel = 'email'
                          AND n.status = 'sent'
                    ) AS email_sent
                FROM anomalies a
                WHERE a.status IN ('open', 'acknowledged')
                ORDER BY a.id DESC
                LIMIT ?
                """,
                (max(1, min(int(limit), 50)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def cleanup(self, *, readings_retention_days, notifications_retention_days, incidents_retention_days, sync_queue_retention_days):
        now = datetime.now(timezone.utc)
        readings_cutoff = (now - timedelta(days=max(1, readings_retention_days))).isoformat()
        notifications_cutoff = (now - timedelta(days=max(1, notifications_retention_days))).isoformat()
        incidents_cutoff = (now - timedelta(days=max(1, incidents_retention_days))).isoformat()
        sync_cutoff = (now - timedelta(days=max(1, sync_queue_retention_days))).isoformat()

        with self.connect() as connection:
            active_or_recent_reading_ids = {
                row["reading_id"]
                for row in connection.execute(
                    """
                    SELECT reading_id
                    FROM anomalies
                    WHERE reading_id IS NOT NULL
                      AND (
                        status IN ('open', 'acknowledged', 'in_progress')
                        OR created_at >= ?
                      )
                    """,
                    (incidents_cutoff,),
                ).fetchall()
            }
            old_reading_rows = connection.execute(
                "SELECT id FROM readings WHERE created_at < ?",
                (readings_cutoff,),
            ).fetchall()
            removable_reading_ids = [
                row["id"]
                for row in old_reading_rows
                if row["id"] not in active_or_recent_reading_ids
            ]

            if removable_reading_ids:
                placeholders = ",".join("?" for _ in removable_reading_ids)
                connection.execute(
                    f"DELETE FROM sync_queue WHERE reading_id IN ({placeholders}) AND status != 'pending' AND status != 'failed' AND status != 'retrying'",
                    removable_reading_ids,
                )
                connection.execute(
                    f"DELETE FROM readings WHERE id IN ({placeholders})",
                    removable_reading_ids,
                )

            connection.execute(
                """
                DELETE FROM notification_log
                WHERE created_at < ?
                  AND anomaly_id NOT IN (
                    SELECT id FROM anomalies WHERE status IN ('open', 'acknowledged', 'in_progress')
                  )
                """,
                (notifications_cutoff,),
            )
            connection.execute(
                """
                DELETE FROM incident_events
                WHERE created_at < ?
                  AND anomaly_id IN (
                    SELECT id FROM anomalies WHERE status IN ('resolved', 'false_positive')
                  )
                """,
                (incidents_cutoff,),
            )
            connection.execute(
                """
                DELETE FROM anomalies
                WHERE created_at < ?
                  AND status IN ('resolved', 'false_positive')
                """,
                (incidents_cutoff,),
            )
            connection.execute(
                """
                DELETE FROM sync_queue
                WHERE synced_at < ?
                  AND status = 'synced'
                """,
                (sync_cutoff,),
            )

        with self.connect() as connection:
            connection.execute("VACUUM")

    @staticmethod
    def _serialize(row):
        return {
            "id": row["id"], "reading_uuid": row["reading_uuid"], "created_at": row["created_at"], "node_id": row["node_id"],
            "volume_m3": row["volume_m3"], "capacity_percent": row["capacity_percent"],
            "confidence_percent": row["confidence_percent"], "valid_zones": row["valid_zones"],
            "status": row["status"], "alerts": json.loads(row["alerts_json"]),
            "height_grid_m": json.loads(row["grid_json"]),
            "scenario": row["scenario"], "reference_percent": row["reference_percent"],
            "reference_error_points": row["reference_error_points"],
            "average_height_m": row["average_height_m"],
            "maximum_height_m": row["maximum_height_m"], "capacity_m3": row["capacity_m3"],
            "box_id": row["box_id"] or row["node_id"], "sensor_id": row["sensor_id"] or row["node_id"],
            "material_type": row["material_type"] or "nao_informado", "material_name": row["material_name"] or "Não informado",
            "density_t_m3": row["density_t_m3"], "expected_volume_m3": row["expected_volume_m3"],
            "estimated_tons": row["estimated_tons"], "reading_duration_ms": row["reading_duration_ms"],
        }
