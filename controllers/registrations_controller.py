from flask import Blueprint, jsonify, request, abort
from main import db, bcrypt, jwt
from models.registrations import Registration
from schemas.registration_schema import registration_schema, registrations_schema
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, jwt_required

registrations = Blueprint('registrations', __name__, url_prefix='/registrations')

# a route to view all races, should be admin only
@registrations.route('/', methods = ['GET'])
def get_races():
    # query all registrations from the database
    registrations_list = Registration.query.all()
    # convert to json format
    result = registrations_schema.dump(registrations_list)
    # return the result
    return jsonify(result)





# a route to view all participants under a race

# register 
# need to check if the participant is already registered, can automatically assign gender and age group
# check if field limit is exceeded