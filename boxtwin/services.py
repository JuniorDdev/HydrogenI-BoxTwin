import json
from pathlib import Path

import numpy as np


class CalibrationService:
    def __init__(self, path):
        self.path = Path(path)

    def save(self, distance_grid_mm):
        payload = {"version": 1, "empty_distance_grid_mm": distance_grid_mm}
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def load(self):
        if not self.path.exists():
            return None
        return json.loads(self.path.read_text(encoding="utf-8"))["empty_distance_grid_mm"]


class VolumeService:
    def __init__(self, length_m, width_m, height_m):
        self.length_m = length_m
        self.width_m = width_m
        self.height_m = height_m
        self.capacity_m3 = length_m * width_m * height_m
        self.cell_area_m2 = (length_m * width_m) / 64

    def calculate(self, empty_grid_mm, current_grid_mm):
        empty = np.array(empty_grid_mm, dtype=float)
        current = np.array([[np.nan if value is None else value for value in row] for row in current_grid_mm])
        heights = np.clip((empty - current) / 1000, 0, self.height_m)
        valid = np.isfinite(heights)
        valid_zones = int(valid.sum())
        volume_m3 = float(np.nansum(heights) * self.cell_area_m2)
        capacity_percent = (volume_m3 / self.capacity_m3 * 100) if self.capacity_m3 else 0
        coverage = valid_zones / 64
        confidence_percent = round(coverage * 100, 1)
        safe_heights = np.where(valid, heights, 0).round(4).tolist()
        return {
            "volume_m3": round(volume_m3, 5),
            "capacity_percent": round(capacity_percent, 1),
            "confidence_percent": confidence_percent,
            "valid_zones": valid_zones,
            "height_grid_m": safe_heights,
        }


class AlertService:
    def __init__(self, capacity_limit, confidence_min):
        self.capacity_limit = capacity_limit
        self.confidence_min = confidence_min

    def evaluate(self, metrics):
        alerts = []
        if metrics["capacity_percent"] >= self.capacity_limit:
            alerts.append({"type": "capacity", "level": "warning", "message": "Capacidade próxima do limite."})
        if metrics["confidence_percent"] < self.confidence_min:
            alerts.append({"type": "confidence", "level": "danger", "message": "Confiança baixa; verificar sensor."})
        if metrics["valid_zones"] < 48:
            alerts.append({"type": "obstruction", "level": "danger", "message": "Possível obstrução ou perda de zonas."})
        return alerts

