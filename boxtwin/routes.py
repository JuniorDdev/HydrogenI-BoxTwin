import json
import time
import base64
import hashlib
import hmac
from datetime import datetime, timezone
from functools import wraps
from io import BytesIO

from flask import Blueprint, Response, current_app, jsonify, redirect, render_template, request, send_file, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .reports import build_operational_report

bp = Blueprint("main", __name__)


def runtime():
    return current_app.extensions["boxtwin_runtime"]


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Autenticação administrativa necessária."}), 401
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


@bp.get("/")
def landing():
    return render_template("index.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/simulador")
def simulator():
    return render_template("simulator.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        expected = current_app.config["ADMIN_PASSWORD"]
        password_ok = check_password_hash(expected, password) if expected.startswith(("pbkdf2:", "scrypt:")) else password == expected
        if username == current_app.config["ADMIN_USERNAME"] and password_ok:
            session.clear()
            session["admin_authenticated"] = True
            return redirect(url_for("main.admin"))
        error = "Usuário ou senha inválidos."
    return render_template("login.html", error=error)


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.get("/admin")
@admin_required
def admin():
    return render_template("admin.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/api/admin/summary")
@admin_required
def admin_summary():
    readings = runtime().database.history(100)
    anomaly_items = runtime().database.anomalies(500)
    active_statuses = {"open", "acknowledged", "in_progress"}
    latest_reading = readings[-1] if readings else None
    return jsonify({
        "latest": latest_reading,
        "readings_count": len(readings),
        "active_incidents": sum(item["status"] in active_statuses for item in anomaly_items),
        "resolved_incidents": sum(item["status"] == "resolved" for item in anomaly_items),
        "average_confidence": round(sum(item["confidence_percent"] for item in readings) / len(readings), 1) if readings else None,
        "sensor_mode": current_app.config["SENSOR_MODE"],
    })


@bp.get("/admin/reports/operational.pdf")
@admin_required
def operational_report():
    try:
        limit = max(10, min(int(request.args.get("limit", 50)), 100))
    except ValueError:
        limit = 50
    readings = runtime().database.history(limit)
    anomaly_items = runtime().database.anomalies(limit)
    pdf_bytes = build_operational_report(
        box_name=current_app.config["BOX_NAME"],
        node_id=current_app.config["BOX_NODE_ID"],
        sensor_mode=current_app.config["SENSOR_MODE"],
        dimensions={
            "length": runtime().volume.length_m,
            "width": runtime().volume.width_m,
            "height": runtime().volume.height_m,
        },
        readings=readings,
        anomalies=anomaly_items,
    )
    filename = f"relatorio_boxtwin_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.pdf"
    response = send_file(BytesIO(pdf_bytes), mimetype="application/pdf", as_attachment=True, download_name=filename)
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/admin/anomalies/<int:anomaly_id>")
@admin_required
def anomaly_page(anomaly_id):
    if not runtime().database.anomaly_detail(anomaly_id):
        return "Anomalia não encontrada.", 404
    return render_template("anomaly.html", anomaly_id=anomaly_id)


@bp.get("/api/health")
def health():
    volume = runtime().volume
    return jsonify({
        "status": "online",
        "node_id": current_app.config["BOX_NODE_ID"],
        "box_name": current_app.config["BOX_NAME"],
        "sensor_mode": current_app.config["SENSOR_MODE"],
        "demo_enabled": hasattr(runtime().sensor, "set_scenario"),
        "dimensions_m": {
            "length": volume.length_m,
            "width": volume.width_m,
            "height": volume.height_m,
        },
        "capacity_m3": volume.capacity_m3,
    })


@bp.post("/api/calibration")
def calibrate():
    return jsonify(runtime().calibrate())


@bp.post("/api/readings")
def capture():
    result = runtime().capture()
    return jsonify(result), 409 if result.get("status") == "not_calibrated" else 201


@bp.get("/api/readings/latest")
def latest():
    return jsonify(runtime().database.latest() or {"status": "no_data"})


@bp.get("/api/readings/history")
def history():
    return jsonify(runtime().database.history(request.args.get("limit", 50)))


@bp.get("/api/stream")
def stream():
    # Captura o runtime fora do gerador, evitando erro de contexto
    rt = runtime()

    def events():
        last_id = None
        while True:
            reading = rt.database.latest()
            if reading and reading["id"] != last_id:
                last_id = reading["id"]
                yield f"event: reading\ndata: {json.dumps(reading)}\n\n"
            else:
                yield ": keep-alive\n\n"
            time.sleep(2)

    return Response(events(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no"
    })


@bp.get("/api/admin/anomalies")
@admin_required
def anomalies():
    return jsonify(runtime().database.anomalies(request.args.get("limit", 100), request.args.get("status")))


@bp.post("/api/admin/anomalies/<int:anomaly_id>/acknowledge")
@admin_required
def acknowledge(anomaly_id):
    payload = request.get_json(silent=True) or {}
    if not runtime().database.acknowledge_anomaly(anomaly_id, payload.get("note", "")):
        return jsonify({"error": "Anomalia não encontrada."}), 404
    return jsonify({"ok": True, "id": anomaly_id})


@bp.get("/api/admin/anomalies/<int:anomaly_id>")
@admin_required
def anomaly_detail(anomaly_id):
    detail = runtime().database.anomaly_detail(anomaly_id)
    return (jsonify(detail), 200) if detail else (jsonify({"error": "Anomalia não encontrada."}), 404)


@bp.post("/api/admin/anomalies/<int:anomaly_id>/status")
@admin_required
def anomaly_status(anomaly_id):
    payload = request.get_json(silent=True) or {}
    try:
        found = runtime().database.update_anomaly_status(anomaly_id, payload.get("status", ""), payload.get("note", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return (jsonify({"ok": True}), 200) if found else (jsonify({"error": "Anomalia não encontrada."}), 404)


@bp.route("/api/admin/recipients", methods=["GET", "POST"])
@admin_required
def recipients():
    if request.method == "GET":
        return jsonify(runtime().database.recipients())
    payload = request.get_json(silent=True) or {}
    if not str(payload.get("name", "")).strip() or (not payload.get("email") and not payload.get("phone")):
        return jsonify({"error": "Informe nome e ao menos e-mail ou telefone."}), 400
    return jsonify({"id": runtime().database.save_recipient(payload)}), 201


@bp.route("/api/admin/rules", methods=["GET", "POST"])
@admin_required
def rules():
    if request.method == "GET":
        return jsonify(runtime().database.rules())
    payload = request.get_json(silent=True) or {}
    if payload.get("channel") not in {"email", "twilio"} or not payload.get("recipient_id"):
        return jsonify({"error": "Destinatário e canal válido são obrigatórios."}), 400
    payload.setdefault("anomaly_type", "*")
    return jsonify({"id": runtime().database.save_rule(payload)}), 201


@bp.get("/api/admin/notifications")
@admin_required
def notifications():
    return jsonify(runtime().database.notification_history(request.args.get("limit", 100)))


@bp.post("/api/admin/assistant")
@admin_required
def assistant():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"error": "Informe uma pergunta."}), 400
    if len(question) > 1200:
        return jsonify({"error": "A pergunta deve ter no máximo 1.200 caracteres."}), 400
    context = payload.get("context")
    if context is None:
        latest_reading = runtime().database.latest()
        if latest_reading:
            latest_reading = {key: value for key, value in latest_reading.items() if key != "height_grid_m"}
        context = {
            "latest_reading": latest_reading,
            "active_anomalies": runtime().database.anomalies(10, "open"),
        }
    history = [
        {"question": str(turn.get("question", ""))[:1200], "answer": str(turn.get("answer", ""))[:2000]}
        for turn in (payload.get("history") or [])
        if isinstance(turn, dict)
    ][-6:]
    return jsonify(runtime().assistant.answer(question, context, history))


def valid_twilio_signature():
    if not current_app.config["TWILIO_VALIDATE_SIGNATURE"]:
        return True
    signature = request.headers.get("X-Twilio-Signature", "")
    token = current_app.config["TWILIO_AUTH_TOKEN"]
    if not signature or not token:
        return False
    public_url = current_app.config["PUBLIC_BASE_URL"] + request.path
    material = public_url + "".join(key + value for key in sorted(request.form) for value in request.form.getlist(key))
    expected = base64.b64encode(hmac.new(token.encode(), material.encode(), hashlib.sha1).digest()).decode()
    return hmac.compare_digest(signature, expected)


@bp.post("/api/webhooks/twilio/status")
def twilio_status():
    if not valid_twilio_signature():
        return "Invalid signature", 403
    sid, status = request.form.get("MessageSid", ""), request.form.get("MessageStatus", "")
    runtime().database.update_delivery_status(sid, status, request.form.get("ErrorMessage", ""))
    return "", 204


@bp.post("/api/webhooks/twilio/incoming")
def twilio_incoming():
    if not valid_twilio_signature():
        return "Invalid signature", 403
    parts = request.form.get("Body", "").strip().split()
    action = {"1": "acknowledged", "2": "in_progress", "3": "resolved"}.get(parts[0] if parts else "")
    if not action or len(parts) < 2 or not parts[1].isdigit():
        reply = "Formato inválido. Responda 1 ID para ciência, 2 ID para atendimento ou 3 ID para resolver."
    else:
        anomaly_id = int(parts[1])
        sender = request.form.get("From", "Responsável via Twilio")
        found = runtime().database.update_anomaly_status(anomaly_id, action, "Atualização recebida pelo WhatsApp/SMS.", sender)
        reply = f"BoxTwin #{anomaly_id} atualizado para {action}." if found else "Anomalia não encontrada."
    escaped = reply.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped}</Message></Response>', 200, {"Content-Type": "application/xml"}


@bp.get("/manifest.webmanifest")
def manifest():
    return current_app.send_static_file("manifest.webmanifest")


@bp.get("/service-worker.js")
def service_worker():
    return current_app.send_static_file("service-worker.js")


@bp.post("/api/demo/level/<float:level>")
def demo_level(level):
    sensor = runtime().sensor
    if not hasattr(sensor, "set_level"):
        return jsonify({"error": "Disponível somente no modo mock."}), 400
    sensor.set_level(level)
    return jsonify({"level_percent": sensor.level_percent})


@bp.get("/api/demo/scenarios")
def demo_scenarios():
    sensor = runtime().sensor
    if not hasattr(sensor, "list_scenarios"):
        return jsonify({"error": "Disponível somente no modo simulado."}), 400
    return jsonify({"scenarios": sensor.list_scenarios(), "active": sensor.scenario})


@bp.post("/api/demo/scenario/<scenario>")
def demo_scenario(scenario):
    sensor = runtime().sensor
    if not hasattr(sensor, "set_scenario"):
        return jsonify({"error": "Disponível somente no modo simulado."}), 400
    try:
        sensor.set_scenario(scenario)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    if scenario == "empty":
        runtime().calibrate()
    result = runtime().capture()
    return jsonify(result), 201


@bp.post("/api/demo/setup")
def demo_setup():
    sensor = runtime().sensor
    if not hasattr(sensor, "set_scenario"):
        return jsonify({"error": "Disponível somente no modo simulado."}), 400
    sensor.set_scenario("empty")
    calibration = runtime().calibrate()
    sensor.set_scenario("pile")
    reading = runtime().capture()
    return jsonify({"calibration": calibration, "reading": reading}), 201