from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    # Creating the flask app object
    app = Flask(__name__)

    # configuring app:
    app.config.from_object("config.app_config")

    # creating database object, This allows us to use ORM
    db.init_app(app)

    #creating the jwt and bcrypt objects, this allows us to use authentication
    bcrypt.init_app(app)

    from commands import db_commands
    app.register_blueprint(db_commands)

    return app