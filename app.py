from __init__ import create_app


app = create_app()

APP_PORT = app.config["APP_PORT"]

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=APP_PORT, threaded=True)
