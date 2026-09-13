from subprocess import CompletedProcess

from boxtwin.sensors.vl53l8cx import VL53L8CXSensor


def _frame(status_overrides=None):
    status_overrides = status_overrides or {}
    lines = []
    for zone in range(64):
        status = status_overrides.get(zone, 5)
        lines.append(f"Zone : {zone}, Status : {status}, Distance : {1000 + zone} mm")
    return "\n".join(lines)


def test_reads_last_complete_8x8_frame(tmp_path):
    binary = tmp_path / "menu"
    binary.touch()
    output = _frame() + "\n" + _frame({9: 255})

    def runner(*args, **kwargs):
        assert kwargs["input"] == "2\n12\n"
        return CompletedProcess(args[0], 0, output, "")

    sensor = VL53L8CXSensor(binary, runner=runner)
    grid = sensor.read_distance_grid_mm()

    assert len(grid) == 8
    assert all(len(row) == 8 for row in grid)
    assert grid[0][0] == 1000
    assert grid[1][1] is None
