from flask import Flask, jsonify
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Basic config placeholder
    app.config.from_object("config.Config")

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "version": "1.0"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=app.config.get("DEBUG", False))
