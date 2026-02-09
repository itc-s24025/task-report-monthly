from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from app.config import Config
from flask_migrate import Migrate

db = SQLAlchemy()
oauth = OAuth()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    oauth.init_app(app)

    # ✅ OAuth
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # register API blueprints
    from app.routes.category import category_bp
    app.register_blueprint(category_bp)

    from app.routes.task import task_bp
    app.register_blueprint(task_bp)

    Migrate(app, db)

    return app

