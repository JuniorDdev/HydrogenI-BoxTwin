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
        self.sensor = build_sensor(config["SENSOR_MODE"], config["BOX_HEIGHT_M"])
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

    def calibrate(self):
        grid = self.sensor.read_distance_grid_mm()
        self.calibration.save(grid)
        return {"calibrated": True, "zones": 64, "message": "Linha de base do box vazio salva."}

    def capture(self):
        empty = self.calibration.load()
        if empty is None:
            return {"status": "not_calibrated", "message": "Calibre o box vazio antes de medir."}
        current = self.sensor.read_distance_grid_mm()
        metrics = self.volume.calculate(empty, current)
        reference_percent = getattr(self.sensor, "reference_percent", None)
        reference_error = (
            round(abs(metrics["capacity_percent"] - reference_percent), 2)
            if reference_percent is not None else None
        )
        alerts = self.alerts.evaluate(metrics)
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
        }
        reading_id, created_at = self.database.save_reading(reading)
        reading["created_at"] = created_at
        anomaly_records = self.database.save_anomalies(reading_id, alerts)
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

    def _loop(self):
        # Captura e alerta acontecem só por requisição explícita (botão "Capturar" no simulador,
        # POST /api/readings, ou sincronização de borda) — este laço de fundo NÃO chama self.capture()
        # sozinho. Antes ele capturava automaticamente a cada SAMPLE_INTERVAL_SECONDS, o que gerava
        # alertas/e-mails repetidos sem ninguém ter pedido. As tarefas de manutenção abaixo continuam
        # rodando no mesmo intervalo.
        while not self._stop.is_set():
            try:
                self.notifications.dispatch_escalations()
            except Exception as exc:
                print(f"[BoxTwin] Falha no escalonamento: {exc}")
            try:
                self.edge_sync.process_queue()
            except Exception as exc:
                print(f"[BoxTwin] Falha na sincronização edge/cloud: {exc}")
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
