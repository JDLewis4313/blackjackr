from flask import Flask, url_for
from infrastructure.database import db
from domains.player.auth import auth_bp
from domains.core.routes import core_bp

    
app=Flask(__name__)

db.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(core_bp)


    
if __name__=="__main__":
    app.run(debug=True)
