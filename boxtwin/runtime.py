import threading
import time

from .sensors import build_sensor
from .services import AlertService, CalibrationService, VolumeService


class BoxTwinRuntime:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.sensor = build_sensor(config["SENSOR_MODE"], config["BOX_HEIGHT_M"])
        self.calibration = CalibrationService(config["CALIBRATION_PATH"])
        self.volume = VolumeService(config["BOX_LENGTH_M"], config["BOX_WIDTH_M"], config["BOX_HEIGHT_M"])
        self.alerts = AlertService(config["CAPACITY_ALERT_PERCENT"], config["MIN_CONFIDENCE_PERCENT"])
        self._stop = threading.Event()
        self._thread = None

    def calibrate(self):
        grid = self.sensor.read_distance_grid_mm()
        self.calibration.save(grid)
        return {"calibrated": True, "zones": 64}

    def capture(self):
        empty = self.calibration.load()
        if empty is None:
            return {"status": "not_calibrated", "message": "Calibre o box vazio antes de medir."}
        current = self.sensor.read_distance_grid_mm()
        metrics = self.volume.calculate(empty, current)
        alerts = self.alerts.evaluate(metrics)
        reading = {
            **metrics,
            "node_id": self.config["BOX_NODE_ID"],
            "status": "alert" if alerts else "normal",
            "alerts": alerts,
        }
        reading_id, created_at = self.database.save_reading(reading)
        return {**reading, "id": reading_id, "created_at": created_at}

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, name="boxtwin-capture", daemon=True)
        self._thread.start()

    def _loop(self):
        while not self._stop.is_set():
            try:
                if self.calibration.load() is not None:
                    self.capture()
            except Exception as exc:
                print(f"[BoxTwin] Falha de leitura: {exc}")
            self._stop.wait(self.config["SAMPLE_INTERVAL_SECONDS"])

