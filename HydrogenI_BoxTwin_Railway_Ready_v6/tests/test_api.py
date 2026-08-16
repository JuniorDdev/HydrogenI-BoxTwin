import pytest

from boxtwin import create_app


def test_health(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "online"


def test_demo_setup_and_scenario(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    client = app.test_client()

    setup = client.post("/api/demo/setup")
    assert setup.status_code == 201
    assert setup.get_json()["reading"]["scenario"] == "pile"

    reading = client.post("/api/demo/scenario/flat_50")
    assert reading.status_code == 201
    payload = reading.get_json()
    assert payload["capacity_percent"] == pytest.approx(50, abs=0.2)
    assert payload["reference_error_points"] <= 0.2

    latest = client.get("/api/readings/latest").get_json()
    assert latest["scenario"] == "flat_50"

    obstruction = client.post("/api/demo/scenario/obstruction").get_json()
    assert obstruction["confidence_percent"] < 70
    assert any(alert["type"] == "obstruction" for alert in obstruction["alerts"])


def test_invalid_demo_scenario(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    response = app.test_client().post("/api/demo/scenario/inexistente")
    assert response.status_code == 404
