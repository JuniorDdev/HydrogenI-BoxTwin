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
                "data_source": "TEXT",
                "observed_volume_m3": "REAL",
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
                CREATE TABLE IF NOT EXISTS box_nodes (
                    node_id TEXT PRIMARY KEY,
                    last_seen_at TEXT NOT NULL,
                    last_reading_at TEXT,
                    last_sync_at TEXT,
                    sensor_status TEXT NOT NULL DEFAULT 'unknown',
                    api_status TEXT NOT NULL DEFAULT 'unknown',
                    sensor_mode TEXT,
                    details_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS edge_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_uuid TEXT NOT NULL UNIQUE,
                    node_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    requested_at TEXT NOT NULL,
                    requested_by TEXT,
                    claimed_at TEXT,
                    finished_at TEXT,
                    result_json TEXT,
                    error_message TEXT
                );
                CREATE TABLE IF NOT EXISTS edge_command_results (
                    command_uuid TEXT PRIMARY KEY,
                    node_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT
                );
                CREATE TABLE IF NOT EXISTS runtime_settings (
                    setting_key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)
            command_columns = {row[1] for row in connection.execute("PRAGMA table_info(edge_commands)")}
            if "payload_json" not in command_columns:
                connection.execute("ALTER TABLE edge_commands ADD COLUMN payload_json TEXT")
            notification_columns = {row[1] for row in connection.execute("PRAGMA table_info(notification_log)")}
            for column in ("provider_message_id", "delivery_status", "recipient_id"):
                if column not in notification_columns:
                    connection.execute(f"ALTER TABLE notification_log ADD COLUMN {column} {'INTEGER' if column == 'recipient_id' else 'TEXT'}")
            connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_readings_uuid ON readings(reading_uuid)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status, id)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_readings_created_at ON readings(created_at)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_readings_box_material ON readings(box_id, material_type)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_edge_commands_node_status ON edge_commands(node_id, status, id)")
            # Versões anteriores gravavam os alertas dentro da leitura sincronizada,
            # mas não os materializavam na lista operacional do Railway.
            readings = connection.execute("SELECT id, created_at, alerts_json FROM readings").fetchall()
            for reading in readings:
                try:
                    alerts = json.loads(reading["alerts_json"] or "[]")
                except json.JSONDecodeError:
                    alerts = []
                for alert in alerts:
                    alert_type = str(alert.get("type", "unknown"))
                    message = str(alert.get("message", "Alerta sem descrição."))
                    exists = connection.execute(
                        "SELECT 1 FROM anomalies WHERE reading_id=? AND anomaly_type=? AND message=? LIMIT 1",
                        (reading["id"], alert_type, message),
                    ).fetchone()
                    if not exists:
                        connection.execute(
                            "INSERT INTO anomalies (created_at, reading_id, anomaly_type, severity, message) VALUES (?, ?, ?, ?, ?)",
                            (reading["created_at"], reading["id"], alert_type, str(alert.get("level", "warning")), message),
                        )

    @staticmethod
    def _command_payload(row):
        if not row:
            return None
        item = dict(row)
        item["result"] = json.loads(item.pop("result_json") or "null")
        item["payload"] = json.loads(item.pop("payload_json", None) or "{}")
        return item

    def enqueue_command(self, node_id, action, requested_by=None, payload=None):
        from uuid import uuid4
        now = datetime.now(timezone.utc).isoformat()
        command_uuid = str(uuid4())
        with self.connect() as connection:
            connection.execute(
                """INSERT INTO edge_commands (command_uuid, node_id, action, requested_at, requested_by, payload_json)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (command_uuid, node_id, action, now, requested_by,
                 json.dumps(payload or {}, ensure_ascii=False)),
            )
            row = connection.execute("SELECT * FROM edge_commands WHERE command_uuid=?", (command_uuid,)).fetchone()
        return self._command_payload(row)

    def command_gate(self, node_id, cooldown_seconds=30):
        """Prevent overlapping physical operations and rapid repeat requests."""
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM edge_commands WHERE node_id=? ORDER BY id DESC LIMIT 1", (node_id,)
            ).fetchone()
        if not row:
            return {"allowed": True, "cooldown_remaining": 0}
        command = self._command_payload(row)
        if command["status"] in {"pending", "claimed"}:
            return {"allowed": False, "reason": "in_progress", "command": command, "cooldown_remaining": 0}
        try:
            elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(command["requested_at"].replace("Z", "+00:00"))).total_seconds()
        except (TypeError, ValueError):
            elapsed = cooldown_seconds
        remaining = max(0, int(cooldown_seconds - elapsed + 0.999))
        return {"allowed": remaining == 0, "reason": "cooldown" if remaining else None,
                "command": command, "cooldown_remaining": remaining}

    def claim_next_command(self, node_id):
        """Atomically deliver one queued action to the BoxNode polling the central API."""
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM edge_commands WHERE node_id=? AND status='pending' ORDER BY id LIMIT 1",
                (node_id,),
            ).fetchone()
            if not row:
                return None
            connection.execute(
                "UPDATE edge_commands SET status='claimed', claimed_at=? WHERE id=?",
                (now, row["id"]),
            )
            row = connection.execute("SELECT * FROM edge_commands WHERE id=?", (row["id"],)).fetchone()
        return self._command_payload(row)

    def resolve_command(self, command_uuid, node_id, ok, result=None, error_message=None):
        now = datetime.now(timezone.utc).isoformat()
        status = "succeeded" if ok else "failed"
        with self.connect() as connection:
            cursor = connection.execute(
                """UPDATE edge_commands
                   SET status=?, finished_at=?, result_json=?, error_message=?
                   WHERE command_uuid=? AND node_id=? AND status='claimed'""",
                (status, now, json.dumps(result, ensure_ascii=False) if result is not None else None,
                 str(error_message or "")[:1000] or None, command_uuid, node_id),
            )
            if not cursor.rowcount:
                return None
            row = connection.execute("SELECT * FROM edge_commands WHERE command_uuid=?", (command_uuid,)).fetchone()
        return self._command_payload(row)

    def commands_for_node(self, node_id, limit=10):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM edge_commands WHERE node_id=? ORDER BY id DESC LIMIT ?",
                (node_id, max(1, min(int(limit), 50))),
            ).fetchall()
        return [self._command_payload(row) for row in rows]

    def enqueue_command_result(self, command_uuid, node_id, payload):
        with self.connect() as connection:
            connection.execute(
                """INSERT INTO edge_command_results (command_uuid, node_id, payload_json)
                   VALUES (?, ?, ?)
                   ON CONFLICT(command_uuid) DO UPDATE SET payload_json=excluded.payload_json, status='pending'""",
                (command_uuid, node_id, json.dumps(payload, ensure_ascii=False)),
            )

    def command_result_batch(self, limit=20):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM edge_command_results WHERE status IN ('pending', 'failed') ORDER BY rowid LIMIT ?",
                (max(1, min(int(limit), 100)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_command_result_sent(self, command_uuid):
        with self.connect() as connection:
            connection.execute("UPDATE edge_command_results SET status='sent', last_error=NULL WHERE command_uuid=?", (command_uuid,))

    def mark_command_result_failed(self, command_uuid, error_message):
        with self.connect() as connection:
            connection.execute(
                "UPDATE edge_command_results SET status='failed', attempts=attempts+1, last_error=? WHERE command_uuid=?",
                (str(error_message)[:500], command_uuid),
            )

    def heartbeat(self, payload):
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            connection.execute("""
                INSERT INTO box_nodes (node_id, last_seen_at, last_reading_at, last_sync_at, sensor_status, api_status, sensor_mode, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    last_seen_at=excluded.last_seen_at, last_reading_at=COALESCE(excluded.last_reading_at, box_nodes.last_reading_at),
                    last_sync_at=excluded.last_sync_at, sensor_status=excluded.sensor_status, api_status=excluded.api_status,
                    sensor_mode=excluded.sensor_mode, details_json=excluded.details_json
            """, (payload["node_id"], now, payload.get("last_reading_at"), now,
                  payload.get("sensor_status", "unknown"), payload.get("api_status", "online"),
                  payload.get("sensor_mode"), json.dumps(payload, ensure_ascii=False)))
        return self.node_status(payload["node_id"])

    def runtime_setting(self, setting_key, default=None):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT value_json FROM runtime_settings WHERE setting_key=?", (setting_key,)
            ).fetchone()
        return default if not row else json.loads(row["value_json"])

    def set_runtime_setting(self, setting_key, value):
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            connection.execute(
                """INSERT INTO runtime_settings (setting_key, value_json, updated_at) VALUES (?, ?, ?)
                   ON CONFLICT(setting_key) DO UPDATE SET value_json=excluded.value_json, updated_at=excluded.updated_at""",
                (setting_key, json.dumps(value), now),
            )

    def node_status(self, node_id, offline_after_seconds=120):
        with self.connect() as connection:
            node = connection.execute("SELECT * FROM box_nodes WHERE node_id=?", (node_id,)).fetchone()
            reading = connection.execute("SELECT * FROM readings WHERE node_id=? ORDER BY id DESC LIMIT 1", (node_id,)).fetchone()
        if not node and not reading:
            return None
        result = dict(node) if node else {"node_id": node_id, "sensor_status": "unknown", "api_status": "unknown"}
        last_seen = result.get("last_seen_at") or (self._serialize(reading).get("created_at") if reading else None)
        try:
            stale = (datetime.now(timezone.utc) - datetime.fromisoformat(last_seen.replace("Z", "+00:00"))).total_seconds() > offline_after_seconds
        except (AttributeError, ValueError):
            stale = True
        result["node_status"] = "offline" if stale else "online"
        result["latest_reading"] = self._serialize(reading) if reading else None
        result["details"] = json.loads(result.pop("details_json", "{}"))
        return result

    def latest_for_node(self, node_id):
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM readings WHERE node_id=? ORDER BY id DESC LIMIT 1", (node_id,)).fetchone()
        return self._serialize(row) if row else None

    def list_nodes(self, offline_after_seconds=120):
        with self.connect() as connection:
            rows = connection.execute("SELECT node_id FROM box_nodes UNION SELECT DISTINCT node_id FROM readings ORDER BY node_id").fetchall()
        return [self.node_status(row["node_id"], offline_after_seconds) for row in rows]

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
                    estimated_tons, reading_duration_ms, data_source, observed_volume_m3
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                reading.get("data_source") or "physical", reading.get("observed_volume_m3"),
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
        reading_id, created_at = self.save_reading(reading)
        # O Railway mantém sua própria lista operacional de anomalias.
        self.save_anomalies(reading_id, reading.get("alerts", []))
        return reading_id, created_at, True

    def latest(self):
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1").fetchone()
        return self._serialize(row) if row else None

    def history(self, limit=50, node_id=None):
        limit = max(1, min(int(limit), 500))
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM readings WHERE node_id=? ORDER BY id DESC LIMIT ?", (node_id, limit)).fetchall() if node_id else connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [self._serialize(row) for row in reversed(rows)]

    def history_page(self, page=1, page_size=20, node_id=None):
        page, page_size = max(1, int(page)), max(1, min(int(page_size), 100))
        where, params = (" WHERE node_id=?", [node_id]) if node_id else ("", [])
        with self.connect() as connection:
            total = connection.execute(f"SELECT COUNT(*) FROM readings{where}", params).fetchone()[0]
            rows = connection.execute(f"SELECT * FROM readings{where} ORDER BY id DESC LIMIT ? OFFSET ?", [*params, page_size, (page - 1) * page_size]).fetchall()
        return {"items": [self._serialize(row) for row in rows], "page": page, "page_size": page_size, "total": total, "pages": max(1, (total + page_size - 1) // page_size)}

    def anomalies_page(self, page=1, page_size=20, node_id=None, status=None):
        page, page_size = max(1, int(page)), max(1, min(int(page_size), 100)); clauses, params, join = [], [], ""
        if node_id: join = " JOIN readings ON readings.id=anomalies.reading_id"; clauses.append("readings.node_id=?"); params.append(node_id)
        if status: clauses.append("anomalies.status=?"); params.append(status)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self.connect() as connection:
            total = connection.execute(f"SELECT COUNT(*) FROM anomalies{join}{where}", params).fetchone()[0]
            rows = connection.execute(f"SELECT anomalies.* FROM anomalies{join}{where} ORDER BY anomalies.id DESC LIMIT ? OFFSET ?", [*params, page_size, (page-1)*page_size]).fetchall()
        return {"items": [dict(row) for row in rows], "page": page, "page_size": page_size, "total": total, "pages": max(1, (total + page_size - 1) // page_size)}

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
        box_counts = {}
        for item in items:
            box_counts[item["box_id"] or item["node_id"]] = box_counts.get(item["box_id"] or item["node_id"], 0) + 1
        expected_readings = max(0, int(filters.get("expected_reading_count") or 0))
        positive_error_m3 = sum(item["volume_m3"] - item["expected_volume_m3"] for item in expected if item["volume_m3"] > item["expected_volume_m3"])
        negative_error_m3 = sum(item["expected_volume_m3"] - item["volume_m3"] for item in expected if item["volume_m3"] < item["expected_volume_m3"])
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
                "positive_error_m3": round(positive_error_m3, 5), "negative_error_m3": round(negative_error_m3, 5),
                "reused_boxes_count": sum(1 for count in box_counts.values() if count > 1),
                "repeat_reads_count": sum(max(0, count - 1) for count in box_counts.values()),
                "expected_readings": expected_readings,
                "reading_count_difference": len(items) - expected_readings if expected_readings else None,
                "reading_count_anomaly": expected_readings > 0 and len(items) != expected_readings,
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

    def anomalies_for_node(self, node_id, limit=10):
        with self.connect() as connection:
            rows = connection.execute("""SELECT anomalies.* FROM anomalies JOIN readings ON readings.id=anomalies.reading_id
                WHERE readings.node_id=? ORDER BY anomalies.id DESC LIMIT ?""", (node_id, max(1, min(int(limit), 100)))).fetchall()
        return [dict(row) for row in rows]

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

    def notification_history_page(self, page=1, page_size=20):
        page, page_size = max(1, int(page)), max(1, min(int(page_size), 100))
        with self.connect() as connection:
            total = connection.execute("SELECT COUNT(*) FROM notification_log").fetchone()[0]
            rows = connection.execute("SELECT * FROM notification_log ORDER BY id DESC LIMIT ? OFFSET ?", (page_size, (page - 1) * page_size)).fetchall()
        return {"items": [dict(row) for row in rows], "page": page, "page_size": page_size, "total": total, "pages": max(1, (total + page_size - 1) // page_size)}

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
            "data_source": row["data_source"] or "physical", "observed_volume_m3": row["observed_volume_m3"],
        }
