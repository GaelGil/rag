from flask import Flask
from app.config import Config
from app.extensions import db, bcrypt, migrate, socketio
from app.routes import register_routes
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    bcrypt.init_app(app)
    CORS(
        app,
        origins=["http://localhost:5173"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS"],
    )

    with app.app_context():
        from app.user import models as user_models
        from app.chat import models as chat_models

    register_routes(app)
    return app
