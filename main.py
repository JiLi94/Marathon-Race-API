from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def create_app():
    # Creating the flask app object
    app = Flask(__name__)

    # configuring our app:
    app.config.from_object("config.app_config")
    
    # creating our database object, This allows us to use ORM
    db = SQLAlchemy(app)

    return app