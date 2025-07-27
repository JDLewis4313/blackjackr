from flask import Flask
from config.settings import Config
from infrastructure.database.db import db, migrate
from flask_login import LoginManager
from domains.player.models import Player
from domains.player.auth import auth_bp
from domains.core.routes import core_bp
from domains.game.routes import game_bp

login_manager = LoginManager()
login_manager.login_view = 'player_auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Player.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(core_bp)
    app.register_blueprint(game_bp)

    return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
