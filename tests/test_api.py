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
    assert response.headers["Access-Control-Allow-Origin"] == "*"


def test_mobile_app_route(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    response = app.test_client().get("/app")
    assert response.status_code == 200
    assert b"APLICATIVO OPERACIONAL" in response.data
    assert b"Raspberry/local" in response.data


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


def test_edge_ingest_is_idempotent(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
        "EDGE_SYNC_TOKEN": "demo-token",
    })
    client = app.test_client()
    payload = {
        "reading_uuid": "demo-reading-001",
        "node_id": "BOX-DEMO-01",
        "volume_m3": 0.06,
        "capacity_percent": 99.1,
        "confidence_percent": 100.0,
        "valid_zones": 64,
        "status": "alert",
        "alerts": [{"type": "capacity", "level": "warning", "message": "Capacidade próxima do limite."}],
        "height_grid_m": [[0.25 for _ in range(8)] for _ in range(8)],
        "scenario": "flat_50",
        "reference_percent": 50.0,
        "reference_error_points": 0.0,
        "average_height_m": 0.25,
        "maximum_height_m": 0.25,
        "capacity_m3": 0.12,
    }
    first = client.post("/api/edge/readings", json=payload, headers={"Authorization": "Bearer demo-token"})
    second = client.post("/api/edge/readings", json=payload, headers={"Authorization": "Bearer demo-token"})
    assert first.status_code == 201
    assert first.get_json()["created"] is True
    assert second.status_code == 200
    assert second.get_json()["created"] is False
    anomalies = client.get("/api/boxes/BOX-DEMO-01/anomalies").get_json()
    assert len(anomalies) == 1
    assert anomalies[0]["anomaly_type"] == "capacity"


def test_live_grid_is_ingested_and_exposed(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
        "EDGE_SYNC_TOKEN": "demo-token",
    })
    client = app.test_client()
    payload = {
        "node_id": "BOX-RASP-01",
        "captured_at": "2026-09-13T04:00:00+00:00",
        "valid_zones": 64,
        "distance_grid_mm": [[100 + row + column for column in range(8)] for row in range(8)],
    }
    response = client.post("/api/edge/live-grid", json=payload, headers={"Authorization": "Bearer demo-token"})
    assert response.status_code == 201
    stored = client.get("/api/live-grid?node_id=BOX-RASP-01")
    assert stored.status_code == 200
    assert stored.get_json()["distance_grid_mm"] == payload["distance_grid_mm"]
    assert client.get("/gemeo-sensor").status_code == 200


def test_boxnode_heartbeat_authentication_and_dynamic_monitor(tmp_path):
    app = create_app({
        "TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"), "SENSOR_MODE": "mock",
        "EDGE_NODE_TOKENS": {"BOX-01": "box-01-token"}, "NODE_OFFLINE_AFTER_SECONDS": 120,
    })
    client = app.test_client()
    missing = client.post("/api/edge/heartbeat", json={})
    invalid = client.post("/api/edge/heartbeat", json={"node_id": "BOX-01"}, headers={"Authorization": "Bearer wrong"})
    accepted = client.post("/api/edge/heartbeat", json={"node_id": "BOX-01", "sensor_status": "online", "sensor_mode": "vl53l8cx"}, headers={"Authorization": "Bearer box-01-token"})
    assert missing.status_code == 400
    assert invalid.status_code == 403
    assert accepted.status_code == 200
    status = client.get("/api/boxes/BOX-01").get_json()
    assert status["node_status"] == "online"
    assert status["sensor_status"] == "online"
    assert client.get("/box/BOX-01").status_code == 200


def test_remote_commands_are_queued_claimed_and_reported_by_boxnode(tmp_path):
    app = create_app({
        "TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"), "SENSOR_MODE": "mock",
        "EDGE_NODE_TOKENS": {"BOX-01": "box-01-token"}, "REMOTE_COMMAND_COOLDOWN_SECONDS": 0,
    })
    client = app.test_client()
    with client.session_transaction() as session:
        session["admin_authenticated"] = True

    queued = client.post("/api/admin/boxes/BOX-01/commands", json={"action": "capture"})
    assert queued.status_code == 202
    assert client.post("/api/admin/boxes/BOX-01/commands", json={"action": "calibrate"}).status_code == 409
    command_uuid = queued.get_json()["command"]["command_uuid"]
    assert client.get("/api/edge/commands/next?node_id=BOX-01").status_code == 403

    headers = {"Authorization": "Bearer box-01-token"}
    claimed = client.get("/api/edge/commands/next?node_id=BOX-01", headers=headers)
    assert claimed.status_code == 200
    assert claimed.get_json()["command"]["command_uuid"] == command_uuid
    assert claimed.get_json()["command"]["status"] == "claimed"

    finished = client.post(f"/api/edge/commands/{command_uuid}/result", headers=headers, json={
        "node_id": "BOX-01", "ok": True, "result": {"status": "normal"},
    })
    assert finished.status_code == 200
    assert finished.get_json()["command"]["status"] == "succeeded"
    commands = client.get("/api/admin/boxes/BOX-01/commands").get_json()["commands"]
    assert commands[0]["result"] == {"status": "normal"}

    paused = client.post("/api/admin/boxes/BOX-01/commands", json={"action": "pause_monitoring"})
    assert paused.status_code == 202
    pause_uuid = paused.get_json()["command"]["command_uuid"]
    client.get("/api/edge/commands/next?node_id=BOX-01", headers=headers)
    client.post(f"/api/edge/commands/{pause_uuid}/result", headers=headers, json={
        "node_id": "BOX-01", "ok": True, "result": {"status": "paused"},
    })
    resumed = client.post("/api/admin/boxes/BOX-01/commands", json={"action": "resume_monitoring"})
    assert resumed.status_code == 202


def test_local_raw_read_is_cached_for_the_live_twin(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
    })
    client = app.test_client()
    raw = client.get("/api/sensor/grid")
    assert raw.status_code == 200
    cached = client.get("/api/live-grid").get_json()
    assert cached["valid_zones"] == 64
    assert cached["distance_grid_mm"] == raw.get_json()["distance_grid_mm"]


def test_live_monitoring_pause_is_persisted(tmp_path):
    app = create_app({
        "TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"), "SENSOR_MODE": "mock",
    })
    runtime = app.extensions["boxtwin_runtime"]
    runtime.start_live_monitoring()
    assert runtime.set_live_monitoring(False)["status"] == "paused"
    restarted = create_app({
        "TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"), "SENSOR_MODE": "mock",
    }).extensions["boxtwin_runtime"]
    assert restarted.live_monitoring_status()["enabled"] is False
    assert restarted.live_monitoring_status()["started"] is True


def test_calibration_requires_manual_start_for_live_monitoring(tmp_path):
    app = create_app({
        "TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"), "SENSOR_MODE": "mock",
    })
    runtime = app.extensions["boxtwin_runtime"]
    assert runtime.calibrate()["live_monitoring"]["status"] == "waiting_capture"
    result = runtime.capture(distance_grid_mm=[[400 for _ in range(8)] for _ in range(8)])
    assert result["live_monitoring"]["status"] == "waiting_capture"
    assert runtime.set_live_monitoring(True)["status"] == "active"
    assert runtime.calibrate()["live_monitoring"]["status"] == "waiting_capture"


def test_admin_analytics_reports_operational_metadata(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
        "EXPECTED_READING_COUNT": 20,
    })
    client = app.test_client()
    client.post("/api/demo/setup")
    response = client.post("/api/readings", json={"metadata": {
        "box_id": "BOX-01", "sensor_id": "SENSOR-01", "material_type": "granel",
        "material_name": "Fertilizante", "density_t_m3": 1.2, "expected_volume_m3": 0.01,
    }})
    assert response.status_code == 201
    with client.session_transaction() as session:
        session["admin_authenticated"] = True
    analytics = client.get("/api/admin/analytics?box_id=BOX-01&material_type=granel")
    assert analytics.status_code == 200
    payload = analytics.get_json()
    assert payload["kpis"]["readings_count"] == 1
    assert payload["kpis"]["estimated_tons"] > 0
    assert payload["kpis"]["above_expected_count"] == 1
    assert payload["kpis"]["reading_count_anomaly"] is True
    assert payload["kpis"]["reading_count_difference"] == -19
    pdf = client.get("/admin/reports/operational.pdf?box_id=BOX-01")
    spreadsheet = client.get("/admin/reports/operational.xlsx?box_id=BOX-01")
    assert pdf.status_code == 200
    assert pdf.mimetype == "application/pdf"
    assert spreadsheet.status_code == 200
    assert spreadsheet.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def test_paginated_history_identifies_simulated_source(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "page.db"), "CALIBRATION_PATH": str(tmp_path / "calibration.json"), "SENSOR_MODE": "mock"})
    client = app.test_client()
    client.post("/api/simulator/setup")
    for _ in range(3):
        client.post("/api/simulator/scenario/flat_50")
    response = client.get("/api/readings/history/page?node_id=BOX-DEMO-01&page=1&page_size=2")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 4 and data["pages"] == 2 and len(data["items"]) == 2
    assert data["items"][0]["data_source"] == "simulated"
