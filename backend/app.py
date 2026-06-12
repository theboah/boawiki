import os

from api import article,user,link,settings
from models import db

from flask import Flask, app 
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_smorest import Api
import dotenv
import json

#we want to abstract websocket code to the collaboration.py file
#We want to check if running in dev then log for websockets etc

def create_app(): 
    dotenv.load_dotenv()
    app = Flask(__name__)
    app.config["API_TITLE"] = "Boa Wiki API"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
    app.config["API_VERSION"] = os.environ["API_VERSION"] 
    app.config["OPENAPI_VERSION"] = os.environ["OPENAPI_VERSION"]
    app.config["OPENAPI_URL_PREFIX"] = "/" 
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    #Adding Flask extensions
    jwt = JWTManager()
    bcrypt = Bcrypt()
    socketio = SocketIO()
    
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)
    api = Api(app)
    
    #Register blueprints
    api.register_blueprint(article.api)
    api.register_blueprint(user.api)
    api.register_blueprint(link.api)
    api.register_blueprint(settings.api)
    
    # Print all registered endpoints
    print("\n--- Registered Endpoints ---")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    print("----------------------------\n")


    with app.app_context():
        db.create_all()
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)