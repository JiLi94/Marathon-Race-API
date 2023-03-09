from flask import Blueprint, jsonify, request, abort
from main import db, bcrypt, jwt
from models.registrations import Registration
from models.participants import Participant
from controllers.participants_controller import is_admin
from schemas.registration_schema import registration_schema, registrations_schema
from datetime import datetime, timedelta
from flask_jwt_extended import get_jwt_identity, jwt_required
from functools import wraps

registrations = Blueprint('registrations', __name__, url_prefix='/registrations')

# a route to view all races, should be admin only
@registrations.route('/all', methods = ['GET'])
@jwt_required()
@is_admin
def get_registrations():
    # get id of the user
    # id = get_jwt_identity()
    # participant = Participant.query.get(id)
    # # if user does not exist or not admin, return error
    # if not participant or not participant.admin:
    #     return abort(401, description='Invalid User')
    # query all registrations from the database
    registrations_list = Registration.query.all()
    # convert to json format
    result = registrations_schema.dump(registrations_list)
    # return the result
    return jsonify(result)


# add registration
# @registrations.route('/add', methods=['POST'])
# @jwt_required()
# @is_admin
# def add_registration():
#     pass



# a route to view all participants under a race

# register 
# need to check if the participant is already registered, can automatically assign gender and age group
# check if field limit is exceeded