from boxtwin import create_app

app = create_app()

if __name__ == "__main__":
    ssl_context = None
    if app.config.get("SSL_CERT_PATH") and app.config.get("SSL_KEY_PATH"):
        ssl_context = (app.config["SSL_CERT_PATH"], app.config["SSL_KEY_PATH"])
    app.run(
        host=app.config["APP_HOST"],
        port=app.config["APP_PORT"],
        debug=app.config["APP_DEBUG"],
        ssl_context=ssl_context
    )
