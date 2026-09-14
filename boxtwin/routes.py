import json
import time
import base64
import hashlib
import hmac
import re
from datetime import datetime, timezone
from functools import wraps
from io import BytesIO

from flask import Blueprint, Response, current_app, jsonify, redirect, render_template, request, send_file, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .reports import build_operational_report, build_operational_workbook

bp = Blueprint("main", __name__)


PUBLIC_CORS_PATHS = (
    "/api/health",
    "/api/readings",
    "/api/readings/latest",
    "/api/readings/history",
    "/api/alerts/active",
    "/api/calibration",
    "/api/sensor/grid",
    "/api/live-grid",
    "/api/demo/",
)


@bp.after_app_request
def add_public_api_cors_headers(response):
    if not current_app.config.get("APP_CORS_ENABLED", True):
        return response
    if request.path.startswith(PUBLIC_CORS_PATHS):
        response.headers.setdefault("Access-Control-Allow-Origin", "*")
        response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type, Authorization, X-BoxTwin-Token")
        response.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response


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
def group_landing():
    return render_template("group.html")


@bp.get("/projeto")
def landing():
    return render_template("index.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/simulador")
def simulator():
    return render_template("simulator.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/gemeo-sensor")
def live_sensor_twin():
    return render_template("live_twin.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/box/<node_id>")
def box_monitor(node_id):
    return render_template("box_monitor.html", node_id=node_id)


@bp.route("/app", methods=["GET", "OPTIONS"])
@bp.route("/mobile", methods=["GET", "OPTIONS"])
def mobile_app():
    if request.method == "OPTIONS":
        return "", 204
    return render_template("mobile.html")


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
            return redirect(url_for("main.painel"))
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


@bp.get("/painel")
@admin_required
def painel():
    return render_template("painel.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/admin/reports")
@admin_required
def reports_page():
    return render_template("reports.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/admin/analytics")
@admin_required
def analytics_page():
    return render_template("analytics.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


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


@bp.get("/api/admin/analytics")
@admin_required
def admin_analytics():
    return jsonify(runtime().database.analytics(_analytics_filters()))


def _analytics_filters():
    return {
        "sensor_id": request.args.get("sensor_id", ""),
        "box_id": request.args.get("box_id", ""),
        "material_type": request.args.get("material_type", ""),
        "start": request.args.get("start", ""),
        "end": request.args.get("end", ""),
        "expected_reading_count": current_app.config.get("EXPECTED_READING_COUNT", 0),
    }


@bp.get("/admin/reports/operational.pdf")
@admin_required
def operational_report():
    try:
        limit = max(10, min(int(request.args.get("limit", 50)), 100))
    except ValueError:
        limit = 50
    analytics = runtime().database.analytics(_analytics_filters())
    readings = analytics["items"][-limit:]
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
        analytics=analytics,
    )
    filename = f"relatorio_boxtwin_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.pdf"
    response = send_file(BytesIO(pdf_bytes), mimetype="application/pdf", as_attachment=True, download_name=filename)
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/admin/reports/operational.xlsx")
@admin_required
def operational_report_excel():
    try:
        limit = max(10, min(int(request.args.get("limit", 200)), 500))
    except ValueError:
        limit = 200
    analytics = runtime().database.analytics(_analytics_filters())
    readings = analytics["items"][-limit:]
    anomalies = runtime().database.anomalies(limit, request.args.get("status"))
    workbook_bytes = build_operational_workbook(
        box_name=current_app.config["BOX_NAME"],
        node_id=current_app.config["BOX_NODE_ID"],
        sensor_mode=current_app.config["SENSOR_MODE"],
        dimensions={
            "length": runtime().volume.length_m,
            "width": runtime().volume.width_m,
            "height": runtime().volume.height_m,
        },
        readings=readings,
        anomalies=anomalies,
        analytics=analytics,
    )
    filename = f"relatorio_boxtwin_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.xlsx"
    response = send_file(
        BytesIO(workbook_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename,
    )
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


@bp.get("/api/sensor/grid")
def sensor_grid():
    try:
        return jsonify(runtime().read_raw_sensor_grid())
    except RuntimeError as exc:
        return jsonify({"error": str(exc), "status": "sensor_unavailable"}), 503


@bp.get("/api/live-grid")
def live_grid():
    node_id = request.args.get("node_id", "").strip() or None
    return jsonify(runtime().database.latest_live_sensor_grid(node_id) or {"status": "no_data"})


@bp.post("/api/readings")
def capture():
    payload = request.get_json(silent=True) or {}
    result = runtime().capture(payload.get("metadata"))
    return jsonify(result), 409 if result.get("status") == "not_calibrated" else 201


@bp.get("/api/readings/latest")
def latest():
    node_id = request.args.get("node_id", "").strip()
    item = runtime().database.latest_for_node(node_id) if node_id else runtime().database.latest()
    return jsonify(item or {"status": "no_data"})


@bp.get("/api/boxes/<node_id>")
def box_status(node_id):
    return jsonify(runtime().database.node_status(node_id, current_app.config["NODE_OFFLINE_AFTER_SECONDS"]) or {"status": "no_data", "node_id": node_id})


@bp.get("/api/readings/history")
def history():
    return jsonify(runtime().database.history(request.args.get("limit", 50)))


@bp.get("/api/alerts/active")
def active_alerts():
    items = runtime().database.active_alerts(request.args.get("limit", 10))
    return jsonify({
        "count": len(items),
        "items": items,
    })


@bp.get("/api/stream")
def stream():
    # Captura o runtime fora do gerador, evitando erro de contexto
    rt = runtime()
    node_id = request.args.get("node_id", "").strip()

    def events():
        last_id = None
        while True:
            reading = rt.database.latest_for_node(node_id) if node_id else rt.database.latest()
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


@bp.get("/api/admin/reports/summary")
@admin_required
def report_summary():
    resolved_items = runtime().database.anomalies(request.args.get("limit", 200), "closed")
    return jsonify({
        "count": len(resolved_items),
        "items": resolved_items,
    })


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


def valid_edge_token(node_id=None):
    node_tokens = current_app.config.get("EDGE_NODE_TOKENS", {})
    configured = node_tokens.get(node_id) if node_id and node_tokens else current_app.config.get("EDGE_SYNC_TOKEN", "")
    if not configured:
        return False
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        provided = auth_header[7:].strip()
    else:
        provided = request.headers.get("X-BoxTwin-Token", "").strip()
    return hmac.compare_digest(provided, configured)


def parse_twilio_action(form):
    incoming = (
        form.get("ButtonPayload", "").strip()
        or form.get("Body", "").strip()
        or form.get("ButtonText", "").strip()
    )
    normalized = incoming.lower()
    button_match = re.fullmatch(r"(ack|in_progress|resolved)_(\d+)", incoming, re.IGNORECASE)
    if button_match:
        return {
            "ack": "acknowledged",
            "in_progress": "in_progress",
            "resolved": "resolved",
        }[button_match.group(1).lower()], int(button_match.group(2))

    command_match = re.fullmatch(r"([123])(?:\s+(\d+))?", incoming)
    if command_match:
        action = {"1": "acknowledged", "2": "in_progress", "3": "resolved"}[command_match.group(1)]
        anomaly_id = int(command_match.group(2)) if command_match.group(2) else None
        if anomaly_id is None:
            active = runtime().database.anomalies(1, "active")
            if active:
                anomaly_id = active[0]["id"]
        return action, anomaly_id

    action = None
    if re.search(r"\b(1|ok|atendido|atendida|ciente|confirmo|confirmado|visto|ciência|ciencia)\b", normalized):
        action = "acknowledged"
    elif re.search(r"\b(2|atendimento|atender|tratando|andamento|progresso)\b", normalized):
        action = "in_progress"
    elif re.search(r"\b(3|resolvido|resolvida|tratado|tratada|finalizado|finalizada)\b", normalized):
        action = "resolved"

    id_match = re.search(r"#\s*(\d+)|\b(?:id|alerta|boxtwin)\s*(\d+)\b", normalized)
    anomaly_id = int(next(group for group in id_match.groups() if group)) if id_match else None
    if action and anomaly_id is None:
        active = runtime().database.anomalies(1, "active")
        if active:
            anomaly_id = active[0]["id"]
    return action, anomaly_id


@bp.post("/api/webhooks/twilio/status")
def twilio_status():
    if not valid_twilio_signature():
        return "Assinatura inválida.", 403
    sid, status = request.form.get("MessageSid", ""), request.form.get("MessageStatus", "")
    runtime().database.update_delivery_status(sid, status, request.form.get("ErrorMessage", ""))
    return "", 204


@bp.post("/api/webhooks/twilio/incoming")
def twilio_incoming():
    if not valid_twilio_signature():
        return "Assinatura inválida.", 403
    status_labels_pt = {"acknowledged": "ciente", "in_progress": "em atendimento", "resolved": "tratado"}
    next_step = {"open": "acknowledged", "acknowledged": "in_progress", "in_progress": "resolved"}
    next_replies = {
        "acknowledged": 'Próximo passo, responda "em atendimento" ou envie 2.',
        "in_progress": 'Próximo passo, responda "resolvido" ou envie 3.',
        "resolved": "Tratativa encerrada. O alerta foi movido para o relatório.",
    }
    action, anomaly_id = parse_twilio_action(request.form)
    if not action or anomaly_id is None:
        reply = 'Não consegui identificar a tratativa. Responda 1 para "ciente", 2 para "em atendimento" ou 3 para "resolvido".'
    else:
        detail = runtime().database.anomaly_detail(anomaly_id)
        if not detail:
            reply = "Anomalia não encontrada."
        elif detail["anomaly"]["status"] in {"resolved", "false_positive"}:
            reply = f"BoxTwin #{anomaly_id} já está tratado."
        elif next_step.get(detail["anomaly"]["status"]) != action:
            expected = status_labels_pt[next_step[detail["anomaly"]["status"]]]
            reply = f"Para manter o fluxo correto, o próximo passo do BoxTwin #{anomaly_id} é: {expected}."
        else:
            sender = request.form.get("From", "Responsável via Twilio")
            runtime().database.update_anomaly_status(anomaly_id, action, "Atualização recebida pelo WhatsApp/SMS.", sender)
            status_pt = status_labels_pt.get(action, action)
            reply = f"BoxTwin #{anomaly_id} atualizado para {status_pt}. {next_replies[action]}"
    escaped = reply.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped}</Message></Response>', 200, {"Content-Type": "application/xml"}


@bp.get("/api/admin/sync-status")
@admin_required
def sync_status():
    return jsonify(runtime().edge_sync.status())


@bp.post("/api/edge/readings")
def edge_ingest_reading():
    payload = request.get_json(silent=True) or {}
    if not str(payload.get("node_id", "")).strip():
        return jsonify({"accepted": False, "error": "node_id ausente."}), 400
    if not valid_edge_token(str(payload.get("node_id", ""))):
        return jsonify({"accepted": False, "error": "Token inválido."}), 403
    required = {
        "reading_uuid",
        "node_id",
        "volume_m3",
        "capacity_percent",
        "confidence_percent",
        "valid_zones",
        "status",
        "alerts",
        "height_grid_m",
    }
    missing = sorted(key for key in required if key not in payload)
    if missing:
        return jsonify({"accepted": False, "error": f"Campos ausentes: {', '.join(missing)}"}), 400
    reading = {
        "reading_uuid": str(payload["reading_uuid"]),
        "node_id": str(payload["node_id"]),
        "volume_m3": float(payload["volume_m3"]),
        "capacity_percent": float(payload["capacity_percent"]),
        "confidence_percent": float(payload["confidence_percent"]),
        "valid_zones": int(payload["valid_zones"]),
        "status": str(payload["status"]),
        "alerts": payload["alerts"],
        "height_grid_m": payload["height_grid_m"],
        "scenario": payload.get("scenario"),
        "reference_percent": payload.get("reference_percent"),
        "reference_error_points": payload.get("reference_error_points"),
        "average_height_m": payload.get("average_height_m"),
        "maximum_height_m": payload.get("maximum_height_m"),
        "capacity_m3": payload.get("capacity_m3"),
        "box_id": payload.get("box_id"), "sensor_id": payload.get("sensor_id"),
        "material_type": payload.get("material_type"), "material_name": payload.get("material_name"),
        "density_t_m3": payload.get("density_t_m3"), "expected_volume_m3": payload.get("expected_volume_m3"),
        "estimated_tons": payload.get("estimated_tons"), "reading_duration_ms": payload.get("reading_duration_ms"),
    }
    reading_id, created_at, created = runtime().database.ingest_synced_reading(reading)
    runtime().database.heartbeat({"node_id": reading["node_id"], "last_reading_at": created_at, "sensor_status": "online", "api_status": "online"})
    return jsonify({
        "accepted": True,
        "created": created,
        "reading_id": reading_id,
        "reading_uuid": reading["reading_uuid"],
        "created_at": created_at,
    }), 201 if created else 200


@bp.post("/api/edge/live-grid")
def edge_ingest_live_grid():
    payload = request.get_json(silent=True) or {}
    if not str(payload.get("node_id", "")).strip():
        return jsonify({"accepted": False, "error": "node_id ausente."}), 400
    if not valid_edge_token(str(payload.get("node_id", ""))):
        return jsonify({"accepted": False, "error": "Token inválido."}), 403
    required = {"node_id", "captured_at", "valid_zones", "distance_grid_mm"}
    missing = sorted(key for key in required if key not in payload)
    grid = payload.get("distance_grid_mm")
    if missing:
        return jsonify({"accepted": False, "error": f"Campos ausentes: {', '.join(missing)}"}), 400
    if not isinstance(grid, list) or len(grid) != 8 or any(not isinstance(row, list) or len(row) != 8 for row in grid):
        return jsonify({"accepted": False, "error": "A grade deve conter 8 linhas com 8 zonas."}), 400
    stored = runtime().database.upsert_live_sensor_grid({
        "node_id": str(payload["node_id"]),
        "captured_at": str(payload["captured_at"]),
        "valid_zones": int(payload["valid_zones"]),
        "distance_grid_mm": grid,
    })
    runtime().database.heartbeat({"node_id": stored["node_id"], "sensor_status": "online", "api_status": "online"})
    return jsonify({"accepted": True, "status": "stored", "node_id": stored["node_id"], "received_at": stored["received_at"]}), 201


@bp.post("/api/edge/heartbeat")
def edge_heartbeat():
    payload = request.get_json(silent=True) or {}
    node_id = str(payload.get("node_id", "")).strip()
    if not node_id:
        return jsonify({"accepted": False, "error": "node_id ausente."}), 400
    if not valid_edge_token(node_id):
        return jsonify({"accepted": False, "error": "Token inválido."}), 403
    return jsonify({"accepted": True, "node": runtime().database.heartbeat({
        "node_id": node_id,
        "last_reading_at": payload.get("last_reading_at"),
        "sensor_status": payload.get("sensor_status", "unknown"),
        "api_status": "online",
        "sensor_mode": payload.get("sensor_mode"),
    })})


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
