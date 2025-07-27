from flask import Flask
from config.settings import Config
from infrastructure.database.db import db, migrate
from domains.player.auth import auth_bp
from domains.core.routes import core_bp
from domains.game.routes import game_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object('config.settings.Config')


    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp) 
    app.register_blueprint(core_bp)

    return app

app = create_app()
if __name__=="__main__":
    app.run(debug=True)