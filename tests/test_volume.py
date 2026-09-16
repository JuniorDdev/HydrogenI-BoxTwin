import pytest

from boxtwin.services import AlertService, VolumeService


def grid(value):
    return [[value for _ in range(8)] for _ in range(8)]


def test_half_full_box_volume():
    service = VolumeService(length_m=0.40, width_m=0.40, height_m=0.40)
    result = service.calculate(grid(400), grid(200))
    assert result["volume_m3"] == pytest.approx(0.032)
    assert result["capacity_percent"] == pytest.approx(50.0)
    assert result["confidence_percent"] == 97.0
    assert result["zone_quality_percent"] == 100.0


def test_noise_floor_ignores_small_sensor_variation():
    service = VolumeService(length_m=0.145, width_m=0.145, height_m=0.150, noise_floor_m=0.005)
    result = service.calculate(grid(150), grid(146))
    assert result["volume_m3"] == 0
    assert result["capacity_percent"] == 0
    assert all(value == 0 for row in result["height_grid_m"] for value in row)


def test_capacity_alert():
    alerts = AlertService(85, 70).evaluate({"capacity_percent": 90, "confidence_percent": 100, "valid_zones": 64})
    assert alerts[0]["type"] == "capacity"


def test_invalid_grid_shape():
    service = VolumeService(length_m=0.40, width_m=0.40, height_m=0.40)
    with pytest.raises(ValueError):
        service.calculate([[500]], [[250]])


def test_partial_sensor_grid_projects_valid_mean_without_zero_fill():
    service = VolumeService(length_m=0.40, width_m=0.40, height_m=0.40)
    current = grid(200)
    current[0][0] = None
    result = service.calculate(grid(400), current)
    assert result["valid_zones"] == 63
    assert result["confidence_percent"] == pytest.approx(91.1)
    assert result["zone_quality_percent"] == pytest.approx(98.4)
    assert result["average_height_m"] == pytest.approx(0.2)
    assert result["volume_m3"] == pytest.approx(0.032)
    assert result["height_grid_m"][0][0] is None
