import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(app.instance_path, 'app.db')}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from . import models  # noqa
    with app.app_context():
        db.create_all()
    from .views_client import bp as client_bp
    from .views_admin import bp as admin_bp
    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp)

    from .cli import init_db_command
    app.cli.add_command(init_db_command)
    
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
