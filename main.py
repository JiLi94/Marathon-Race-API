from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def create_app():
    # Creating the flask app object
    app = Flask(__name__)

    # configuring app:
    app.config.from_object("config.app_config")

    # creating database object, This allows us to use ORM
    db.init_app(app)

    return app