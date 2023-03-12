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

# a decorator to handle data validation
def validate_input(required_fields=[]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            registration_fields = registration_schema.load(request.json)
            # check if the user input enough information
            for arg in required_fields:
                if arg not in registration_fields:
                    return abort(400, description='Not enough information provided')

            # def a function to validate number
            def validate_num(field_name):
                try:
                    if field_name in registration_fields:
                        if int(registration_fields[field_name]) <= 0:
                            return abort(400, description=f'Please enter a valid number for {field_name}')
                except ValueError:
                    return abort(400, description=f'Please enter a valid number for {field_name}')

            # def a function to validate date or time input
            def validate_datetime(field_name, datetime_format):
                try:
                    if field_name in registration_fields:
                        date_or_time = datetime.strptime(
                            registration_fields[field_name], datetime_format)
                except ValueError:
                    return abort(400, description=f'Please enter a valid date for {field_name} in the format of {datetime_format}')

            # validate all inputs using functions above
            validate_num('participant_id')
            validate_datetime('race_id', '%Y-%m-%d')
            validate_datetime('registration_date', '%H:%M:%S')
            validate_datetime('cut_off_time', '%H:%M:%S')

            return func(*args, **kwargs)
        return wrapper
    return decorator

# a route to view all registrations, should be admin only
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
@registrations.route('/add', methods=['POST'])
@jwt_required()
@is_admin
def add_registration():
    registration_fields = registration_schema.load(request.json)




# a route to view all participants under a race

# register 
# need to check if the participant is already registered, can automatically assign gender and age group
# check if field limit is exceeded