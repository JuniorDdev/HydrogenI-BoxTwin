from flask import Blueprint, current_app, jsonify, render_template, request

bp = Blueprint("main", __name__)


def runtime():
    return current_app.extensions["boxtwin_runtime"]


@bp.get("/")
def dashboard():
    return render_template("index.html", box_name=current_app.config["BOX_NAME"], node_id=current_app.config["BOX_NODE_ID"])


@bp.get("/api/health")
def health():
    return jsonify({"status": "online", "node_id": current_app.config["BOX_NODE_ID"], "sensor_mode": current_app.config["SENSOR_MODE"]})


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


@bp.post("/api/demo/level/<float:level>")
def demo_level(level):
    sensor = runtime().sensor
    if not hasattr(sensor, "set_level"):
        return jsonify({"error": "Disponível somente no modo mock."}), 400
    sensor.set_level(level)
    return jsonify({"level_percent": sensor.level_percent})

