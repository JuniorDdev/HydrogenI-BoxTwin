"""Adapter for the ST VL53L8CX ULD user-space test executable."""

import re
import subprocess
from pathlib import Path

from .base import DepthSensor


_READING = re.compile(
    r"Zone\s*:\s*(?P<zone>\d+)\s*,\s*Status\s*:\s*(?P<status>\d+)\s*,\s*"
    r"Distance\s*:\s*(?P<distance>-?\d+)\s*mm"
)


class VL53L8CXSensor(DepthSensor):
    """Reads the last complete 8x8 frame from the ST ULD menu executable."""

    def __init__(self, menu_path, timeout_seconds=30, runner=subprocess.run):
        self.menu_path = Path(menu_path).expanduser()
        self.timeout_seconds = float(timeout_seconds)
        self._runner = runner
        if not self.menu_path.is_file():
            raise RuntimeError(
                "Executavel VL53L8CX nao encontrado em "
                f"{self.menu_path}. Compile o driver ST em user/test e configure "
                "VL53L8CX_MENU_PATH."
            )

    def read_distance_grid_mm(self):
        try:
            result = self._runner(
                [str(self.menu_path)],
                # Option 2 configures 8x8 ranging. Queue option 12 so the
                # menu exits as soon as the demo returns to it.
                input="2\n12\n",
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Tempo esgotado ao ler o VL53L8CX.") from exc
        except OSError as exc:
            raise RuntimeError(f"Nao foi possivel iniciar o VL53L8CX: {exc}") from exc

        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "sem detalhes").strip()
            raise RuntimeError(f"Driver VL53L8CX terminou com erro: {detail}")

        frames = self._parse_complete_frames(result.stdout)
        if not frames:
            raise RuntimeError("O driver nao retornou uma matriz 8x8 completa.")
        return self._as_grid(frames[-1])

    @staticmethod
    def _parse_complete_frames(output):
        frames, frame = [], {}
        for match in _READING.finditer(output or ""):
            zone = int(match.group("zone"))
            if zone == 0 and frame:
                if len(frame) == 64:
                    frames.append(frame)
                frame = {}
            frame[zone] = (int(match.group("status")), int(match.group("distance")))
            if len(frame) == 64:
                frames.append(frame)
                frame = {}
        return frames

    @staticmethod
    def _as_grid(frame):
        grid = []
        for row in range(8):
            line = []
            for col in range(8):
                status, distance = frame[row * 8 + col]
                line.append(None if status == 255 or distance < 0 else distance)
            grid.append(line)
        return grid
