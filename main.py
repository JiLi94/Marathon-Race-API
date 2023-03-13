from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

db = SQLAlchemy(session_options={"autoflush": False})
bcrypt = Bcrypt()
ma = Marshmallow()
jwt = JWTManager()

def create_app():
    # Creating the flask app object
    app = Flask(__name__)

    # configuring app:
    app.config.from_object("config.app_config")

    # creating database object, This allows us to use ORM
    db.init_app(app)

    #creating the jwt and bcrypt objects, this allows us to use authentication
    bcrypt.init_app(app)

    # creating marshmallow object, this allows us to use schema
    ma.init_app(app)

    # creating JWT object, which allows us to use authentication
    jwt.init_app(app)

    # import controllers and activate blueprints
    from controllers import registrable_controllers
    for controller in registrable_controllers:
        app.register_blueprint(controller)

    # import commands and activate blueprint
    from commands import db_commands
    app.register_blueprint(db_commands)

    return app

