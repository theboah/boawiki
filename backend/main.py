from flask import Flask 
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import dotenv
from api import article,user,folder,link,settings
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(): 
    app = Flask(__name__)
    dotenv.load_dotenv()
    
    db = SQLAlchemy()
    
    app.config['SQLALCHEMY_DATABASE_URI'] = dotenv.get_key(".env", "DATABASE_URL")
    with app.app_context():
        db.create_all()
    
    bcrypt = Bcrypt()
    bcrypt.init_app(app)
    jwt = JWTManager(app)
    
    db.init_app(app)
    
    #Register blueprints
    app.register_blueprint(article.api)
    app.register_blueprint(user.api)
    app.register_blueprint(folder.api)
    app.register_blueprint(link.api)
    app.register_blueprint(settings.api)
    socketio.init_app(app)
    return app

if __name__ == "__main__":
    app = create_app()
    socketio.run(app)