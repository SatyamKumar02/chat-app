# app/__init__.py
from flask import Flask
from config import Config
from .extensions import mongo, login_manager, socketio
from .models import User

# mongo = PyMongo()
# login_manager = LoginManager()
# socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    socketio.init_app(app)

    from .routes.chat import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # 🔌 Import socket event handlers
    from . import socketio_events
    socketio_events.register_socketio_events(socketio)

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)