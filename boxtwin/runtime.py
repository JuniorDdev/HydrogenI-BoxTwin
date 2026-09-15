import threading
from datetime import datetime, timezone
from uuid import uuid4

from .sensors import build_sensor
from pathlib import Path

from .services import AlertService, CalibrationService, EdgeSyncService, GroqService, NotificationService, RagService, VolumeService


class BoxTwinRuntime:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.sensor = build_sensor(config["SENSOR_MODE"], config["BOX_HEIGHT_M"], config)
        self.calibration = CalibrationService(config["CALIBRATION_PATH"])
        self.volume = VolumeService(config["BOX_LENGTH_M"], config["BOX_WIDTH_M"], config["BOX_HEIGHT_M"])
        self.alerts = AlertService(config["CAPACITY_ALERT_PERCENT"], config["MIN_CONFIDENCE_PERCENT"])
        self.rag = RagService(Path(__file__).parent / "knowledge" / "procedures.json")
        self.notifications = NotificationService(config, database, self.rag)
        self.edge_sync = EdgeSyncService(config, database)
        self.assistant = GroqService(config, self.rag)
        self._stop = threading.Event()
        self._thread = None
        self._last_cleanup_date = None
        self._last_heartbeat_at = None
        self._last_command_poll_at = None
        self._sensor_status = "unknown"

    def calibrate(self):
        grid = self.sensor.read_distance_grid_mm()
        self._sensor_status = "online"
        self.calibration.save(grid)
        return {"calibrated": True, "zones": 64, "message": "Linha de base do box vazio salva."}

    def read_raw_sensor_grid(self):
        """Return the physical sensor's distance grid without calibration or volume math."""
        grid = self.sensor.read_distance_grid_mm()
        payload = {
            "node_id": self.config["BOX_NODE_ID"],
            "distance_grid_mm": grid,
            "valid_zones": sum(value is not None for row in grid for value in row),
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
        # O painel local consulta o banco, em vez de iniciar outra leitura física.
        self.database.upsert_live_sensor_grid(payload)
        try:
            sync = self.edge_sync.push_live_grid(payload)
            payload["sync_status"] = sync.get("status", "sent")
        except Exception as exc:
            # A visualização local segue útil mesmo quando a internet do BoxNode cair.
            payload["sync_status"] = "failed"
            payload["sync_error"] = str(exc)[:200]
        return payload

    def capture(self, metadata=None, notify=True, distance_grid_mm=None):
        metadata = metadata or {}
        started_at = datetime.now(timezone.utc)
        empty = self.calibration.load()
        if empty is None:
            return {"status": "not_calibrated", "message": "Calibre o box vazio antes de medir."}
        current = distance_grid_mm if distance_grid_mm is not None else self.sensor.read_distance_grid_mm()
        self._sensor_status = "online"
        metrics = self.volume.calculate(empty, current)
        reference_percent = getattr(self.sensor, "reference_percent", None)
        reference_error = (
            round(abs(metrics["capacity_percent"] - reference_percent), 2)
            if reference_percent is not None else None
        )
        alerts = self.alerts.evaluate(metrics)
        expected_volume_m3 = float(metadata.get("expected_volume_m3") or self.config.get("EXPECTED_VOLUME_M3") or 0)
        if expected_volume_m3:
            difference_percent = (metrics["volume_m3"] - expected_volume_m3) / expected_volume_m3 * 100
            if abs(difference_percent) > 10:
                alerts.append({
                    "type": "expected_volume_deviation",
                    "level": "warning",
                    "message": f"Volume {abs(difference_percent):.1f}% {'acima' if difference_percent > 0 else 'abaixo'} do esperado.",
                })
        density_t_m3 = float(metadata.get("density_t_m3") or self.config.get("MATERIAL_DENSITY_T_M3") or 0)
        reading_uuid = str(uuid4())
        reading = {
            **metrics,
            "reading_uuid": reading_uuid,
            "node_id": self.config["BOX_NODE_ID"],
            "sensor_mode": self.config["SENSOR_MODE"],
            "scenario": getattr(self.sensor, "scenario", "physical"),
            "reference_percent": reference_percent,
            "reference_error_points": reference_error,
            "distance_grid_mm": current,
            "status": "alert" if alerts else "normal",
            "alerts": alerts,
            "box_id": str(metadata.get("box_id") or self.config["BOX_NODE_ID"]),
            "sensor_id": str(metadata.get("sensor_id") or self.config["BOX_NODE_ID"]),
            "material_type": str(metadata.get("material_type") or self.config.get("MATERIAL_TYPE") or "nao_informado"),
            "material_name": str(metadata.get("material_name") or self.config.get("MATERIAL_NAME") or "Não informado"),
            "density_t_m3": density_t_m3 or None,
            "expected_volume_m3": expected_volume_m3 or None,
            "estimated_tons": round(metrics["volume_m3"] * density_t_m3, 4) if density_t_m3 else None,
            "reading_duration_ms": int((datetime.now(timezone.utc) - started_at).total_seconds() * 1000),
        }
        reading_id, created_at = self.database.save_reading(reading)
        reading["created_at"] = created_at
        anomaly_records = self.database.save_anomalies(reading_id, alerts)
        if notify:
            self.notifications.dispatch(anomaly_records)
        sync_payload = {
            **reading,
            "id": reading_id,
            "captured_at": created_at,
            "sync_version": 1,
            "origin": "edge",
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        self.edge_sync.enqueue(reading_id, sync_payload)
        return {**reading, "id": reading_id, "created_at": created_at, "anomaly_ids": [a["id"] for a in anomaly_records]}

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, name="boxtwin-capture", daemon=True)
        self._thread.start()

    def execute_remote_command(self, command):
        """Run a centrally requested action locally, where the sensor and calibration live."""
        action = command.get("action")
        if action == "calibrate":
            result = self.calibrate()
            # Make the freshly calibrated empty surface visible to the central monitor.
            if self.config.get("LIVE_SENSOR_SYNC_ENABLED"):
                self.read_raw_sensor_grid()
            return result
        if action == "capture":
            result = self.capture()
            if result.get("status") == "not_calibrated":
                raise RuntimeError(result["message"])
            # The reading is durable locally first. Sync it immediately when a link exists.
            self.edge_sync.process_queue()
            return result
        raise ValueError(f"Comando remoto não suportado: {action}")

    def report_remote_command(self, command, ok, result=None, error=None):
        """Return the command result now, or persist it locally until the link is restored."""
        try:
            self.edge_sync.complete_command(command["command_uuid"], self.config["BOX_NODE_ID"], ok, result=result, error=error)
        except Exception:
            self.database.enqueue_command_result(command["command_uuid"], self.config["BOX_NODE_ID"], {
                "ok": bool(ok), "result": result, "error": error,
            })

    def _loop(self):
        # A captura automática é opcional. Quando ativada, mantém o painel central atualizado
        # sem disparar repetidamente e-mails/WhatsApp para o mesmo estado.
        while not self._stop.is_set():
            try:
                self.notifications.dispatch_escalations()
            except Exception as exc:
                print(f"[BoxTwin] Falha no escalonamento: {exc}")
            try:
                self.edge_sync.process_queue()
                self.edge_sync.process_command_results()
            except Exception as exc:
                print(f"[BoxTwin] Falha na sincronização edge/cloud: {exc}")
            now = datetime.now(timezone.utc)
            if (not self._last_command_poll_at or
                    (now - self._last_command_poll_at).total_seconds() >= self.config["COMMAND_POLL_INTERVAL_SECONDS"]):
                self._last_command_poll_at = now
                try:
                    command = self.edge_sync.next_command(self.config["BOX_NODE_ID"])
                    if command:
                        print(f"[BoxTwin] Executando comando remoto {command['action']} para {self.config['BOX_NODE_ID']}.")
                        try:
                            result = self.execute_remote_command(command)
                            self.report_remote_command(command, True, result=result)
                        except Exception as exc:
                            self.report_remote_command(command, False, error=str(exc))
                            print(f"[BoxTwin] Comando remoto falhou: {exc}")
                except Exception as exc:
                    print(f"[BoxTwin] Falha ao consultar comandos remotos: {exc}")
            automatic_measurement = self.config.get("LIVE_MEASUREMENT_ENABLED") and self.config["SENSOR_MODE"] == "vl53l8cx"
            if self.config.get("LIVE_SENSOR_SYNC_ENABLED") and not automatic_measurement and self.config["SENSOR_MODE"] == "vl53l8cx":
                try:
                    self.read_raw_sensor_grid()
                except Exception as exc:
                    self._sensor_status = "offline"
                    print(f"[BoxTwin] Falha na leitura bruta ao vivo: {exc}")
            if automatic_measurement:
                if self.calibration.load() is not None:
                    try:
                        self.capture(notify=False)
                        self.edge_sync.process_queue()
                    except Exception as exc:
                        self._sensor_status = "offline"
                        print(f"[BoxTwin] Falha na medição automática: {exc}")
            now = datetime.now(timezone.utc)
            if not self._last_heartbeat_at or (now - self._last_heartbeat_at).total_seconds() >= self.config["HEARTBEAT_INTERVAL_SECONDS"]:
                try:
                    latest = self.database.latest()
                    self.edge_sync.send_heartbeat({
                        "node_id": self.config["BOX_NODE_ID"],
                        "sensor_mode": self.config["SENSOR_MODE"],
                        "sensor_status": self._sensor_status,
                        "last_reading_at": latest.get("created_at") if latest else None,
                    })
                    self._last_heartbeat_at = now
                except Exception as exc:
                    print(f"[BoxTwin] Heartbeat não enviado: {exc}")
            try:
                self.run_cleanup_if_due()
            except Exception as exc:
                print(f"[BoxTwin] Falha na limpeza automática: {exc}")
            self._stop.wait(self.config["SAMPLE_INTERVAL_SECONDS"])

    def run_cleanup_if_due(self):
        if not self.config.get("AUTO_CLEANUP_ENABLED", True):
            return
        today = datetime.now(timezone.utc).date().isoformat()
        if self._last_cleanup_date == today:
            return
        self.database.cleanup(
            readings_retention_days=self.config["READINGS_RETENTION_DAYS"],
            notifications_retention_days=self.config["NOTIFICATIONS_RETENTION_DAYS"],
            incidents_retention_days=self.config["INCIDENTS_RETENTION_DAYS"],
            sync_queue_retention_days=self.config["SYNC_QUEUE_RETENTION_DAYS"],
        )
        self._last_cleanup_date = today
