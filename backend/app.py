from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os


def create_app():
    frontend_path = os.path.join(os.path.dirname(__file__), "../Frontend")
    app = Flask(__name__, template_folder=frontend_path)
    # CORS(app)

    # Basic config placeholder
    app.config.from_object("config.Config")

    from routes.job_routes import jobs_bp
    app.register_blueprint(jobs_bp)

    @app.route('/')
    def about():
        return render_template("index.html", page_name="Job Hunting AI")

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "version": "1.0"})

    return app


if __name__ == "__main__":
    app = create_app()
    # app.run(host="0.0.0.0", port=8000, debug=app.config.get("DEBUG", False))
    app.run(port=8000, debug=app.config.get("DEBUG", False))
