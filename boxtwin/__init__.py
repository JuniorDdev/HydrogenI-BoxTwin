from pathlib import Path

from flask import Flask

from .config import load_config
from .database import Database
from .routes import bp
from .runtime import BoxTwinRuntime


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.update(load_config())
    if test_config:
        app.config.update(test_config)
    app.secret_key = app.config["SECRET_KEY"]

    Path(app.config["DATABASE_PATH"]).parent.mkdir(parents=True, exist_ok=True)
    Path(app.config["CALIBRATION_PATH"]).parent.mkdir(parents=True, exist_ok=True)

    database = Database(app.config["DATABASE_PATH"])
    database.initialize()
    runtime = BoxTwinRuntime(app.config, database)
    app.extensions["boxtwin_runtime"] = runtime
    app.register_blueprint(bp)

    if not app.config.get("TESTING"):
        runtime.start()

    return app

