"""Install the raw VL53L8CX live-reading mode into an existing BoxTwin node."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> None:
    target_root = Path(sys.argv[1] if len(sys.argv) > 1 else "~/HydrogenI-BoxTwin").expanduser()
    source_root = Path(__file__).resolve().parent
    relative_paths = (
        Path("boxtwin/runtime.py"),
        Path("boxtwin/routes.py"),
        Path("boxtwin/database.py"),
        Path("boxtwin/services.py"),
        Path("boxtwin/config.py"),
        Path("boxtwin/static/app.js"),
        Path("boxtwin/static/live-twin.js"),
        Path("boxtwin/templates/live_twin.html"),
        Path("boxtwin/sensors/vl53l8cx.py"),
    )
    for relative in relative_paths:
        source = source_root / relative
        destination = target_root / relative
        if not source.is_file():
            raise SystemExit(f"Arquivo de atualizacao ausente: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_file():
            backup = destination.with_name(destination.name + ".bak-vl53l8cx-live")
            if not backup.exists():
                shutil.copy2(destination, backup)
        shutil.copy2(source, destination)
    print("Modo de leitura ao vivo instalado. Backups terminam com .bak-vl53l8cx-live.")


if __name__ == "__main__":
    main()
