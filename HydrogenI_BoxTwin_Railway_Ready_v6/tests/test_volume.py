import pytest

from boxtwin.services import AlertService, VolumeService


def grid(value):
    return [[value for _ in range(8)] for _ in range(8)]


def test_half_full_box_volume():
    service = VolumeService(length_m=0.60, width_m=0.40, height_m=0.50)
    result = service.calculate(grid(500), grid(250))
    assert result["volume_m3"] == pytest.approx(0.06)
    assert result["capacity_percent"] == pytest.approx(50.0)
    assert result["confidence_percent"] == 100.0


def test_capacity_alert():
    alerts = AlertService(85, 70).evaluate({"capacity_percent": 90, "confidence_percent": 100, "valid_zones": 64})
    assert alerts[0]["type"] == "capacity"


def test_invalid_grid_shape():
    service = VolumeService(length_m=0.60, width_m=0.40, height_m=0.50)
    with pytest.raises(ValueError):
        service.calculate([[500]], [[250]])
