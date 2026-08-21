from boxtwin import create_app


def make_client(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "admin.db"),
        "CALIBRATION_PATH": str(tmp_path / "calibration.json"),
        "SENSOR_MODE": "mock",
        "SECRET_KEY": "test-secret",
        "ADMIN_USERNAME": "admin",
        "ADMIN_PASSWORD": "test-pass",
        "EMAIL_ENABLED": False,
        "TWILIO_ENABLED": False,
        "TWILIO_VALIDATE_SIGNATURE": False,
        "GROQ_ENABLED": False,
    })
    return app.test_client()


def login(client):
    return client.post("/login", data={"username": "admin", "password": "test-pass"})


def test_admin_requires_login(tmp_path):
    response = make_client(tmp_path).get("/admin")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_login_and_rag(tmp_path):
    client = make_client(tmp_path)
    assert login(client).status_code == 302
    response = client.post("/api/admin/assistant", json={"question": "Como tratar obstrução do sensor?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["mode"] == "local-rag"
    assert data["sources"]


def test_public_landing_and_simulator_are_separate(tmp_path):
    client = make_client(tmp_path)
    landing = client.get("/")
    simulator = client.get("/simulador")
    assert landing.status_code == 200
    assert b"Transforme uma pilha irregular" in landing.data
    assert simulator.status_code == 200
    assert b"AMBIENTE SIMULADO" in simulator.data


def test_admin_summary_and_pdf_report(tmp_path):
    client = make_client(tmp_path)
    login(client)
    client.post("/api/demo/setup")
    client.post("/api/demo/scenario/flat_50")
    summary = client.get("/api/admin/summary")
    assert summary.status_code == 200
    assert summary.get_json()["latest"]["capacity_percent"] > 0
    report = client.get("/admin/reports/operational.pdf")
    assert report.status_code == 200
    assert report.mimetype == "application/pdf"
    assert report.data.startswith(b"%PDF")
    assert len(report.data) > 3000


def test_anomaly_workflow(tmp_path):
    client = make_client(tmp_path)
    login(client)
    client.post("/api/demo/setup")
    client.post("/api/demo/scenario/obstruction")
    anomalies = client.get("/api/admin/anomalies").get_json()
    assert anomalies
    open_item = next(item for item in anomalies if item["status"] == "open")
    response = client.post(f"/api/admin/anomalies/{open_item['id']}/acknowledge", json={"note": "Teste"})
    assert response.status_code == 200


def test_recipient_rule_detail_and_twilio_reply(tmp_path):
    client = make_client(tmp_path)
    login(client)
    recipient = client.post("/api/admin/recipients", json={"name": "Equipe de manutenção", "recipient_type": "team", "phone": "whatsapp:+5598999999999"})
    assert recipient.status_code == 201
    rule = client.post("/api/admin/rules", json={"anomaly_type": "obstruction", "recipient_id": recipient.get_json()["id"], "channel": "twilio", "escalation_minutes": 10})
    assert rule.status_code == 201
    client.post("/api/demo/setup")
    reading = client.post("/api/demo/scenario/obstruction").get_json()
    anomaly_id = reading["anomaly_ids"][0]
    assert client.get(f"/api/admin/anomalies/{anomaly_id}").status_code == 200
    reply = client.post("/api/webhooks/twilio/incoming", data={"Body": f"2 {anomaly_id}", "From": "whatsapp:+5598999999999"})
    assert reply.status_code == 200
    detail = client.get(f"/api/admin/anomalies/{anomaly_id}").get_json()
    assert detail["anomaly"]["status"] == "open"

    reply = client.post(
        "/api/webhooks/twilio/incoming",
        data={"Body": f"Alerta BoxTwin #{anomaly_id}\nCapacidade próxima do limite.\nCiente", "From": "whatsapp:+5598999999999"},
    )
    assert reply.status_code == 200
    detail = client.get(f"/api/admin/anomalies/{anomaly_id}").get_json()
    assert detail["anomaly"]["status"] == "acknowledged"

    reply = client.post("/api/webhooks/twilio/incoming", data={"Body": f"2 {anomaly_id}", "From": "whatsapp:+5598999999999"})
    assert reply.status_code == 200
    detail = client.get(f"/api/admin/anomalies/{anomaly_id}").get_json()
    assert detail["anomaly"]["status"] == "in_progress"

    button_reply = client.post(
        "/api/webhooks/twilio/incoming",
        data={"ButtonPayload": f"resolved_{anomaly_id}", "ButtonText": "Resolvido", "From": "whatsapp:+5598999999999"},
    )
    assert button_reply.status_code == 200
    detail = client.get(f"/api/admin/anomalies/{anomaly_id}").get_json()
    assert detail["anomaly"]["status"] == "resolved"


def test_admin_sync_status(tmp_path):
    client = make_client(tmp_path)
    login(client)
    response = client.get("/api/admin/sync-status")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["pending"] == 0
    assert payload["synced"] == 0
    assert payload["enabled"] is False


def test_duplicate_notification_rule_is_reused(tmp_path):
    client = make_client(tmp_path)
    login(client)
    recipient = client.post("/api/admin/recipients", json={"name": "Operação", "email": "operacao@example.com"}).get_json()
    rule = {"anomaly_type": "*", "severity": "*", "recipient_id": recipient["id"], "channel": "email", "escalation_minutes": 0}
    first = client.post("/api/admin/rules", json=rule)
    second = client.post("/api/admin/rules", json=rule)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.get_json()["id"] == second.get_json()["id"]
    assert len(client.get("/api/admin/rules").get_json()) == 1
