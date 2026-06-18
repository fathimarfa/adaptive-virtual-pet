from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    socketio.init_app(app)

    from app.auth import auth_bp
    from app.pet import pet_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(pet_bp, url_prefix='/pet')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()

    return app
