from flask import Blueprint, jsonify, request, abort
from main import db, bcrypt, jwt
from models.races import Race
from models.participants import Participant
from schemas.race_schema import race_schema, races_schema
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

races = Blueprint('races', __name__, url_prefix='/races')

# a decorator to handle data validation
def validate_input(required_fields=[]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            race_fields = race_schema.load(request.json)
            # check if the user input enough information
            for arg in required_fields:
                if arg not in race_fields:
                    return abort(400, description='Not enough information provided')
            
            # def a function to validate number
            def validate_num(field_name):
                try:
                    if field_name in race_fields:
                        if float(race_fields[field_name]) <= 0:
                            return abort(400, description=f'Please enter a valid number for {field_name}')
                except ValueError:
                    return abort(400, description=f'Please enter a valid number for {field_name}')

            # def a function to validate date or time input
            def validate_datetime(field_name, datetime_format):
                try:
                    if field_name in race_fields:
                        date_or_time = datetime.strptime(race_fields[field_name], datetime_format)
                except ValueError:
                    return abort(400, description=f'Please enter a valid date for {field_name} in the format of {datetime_format}')

            # validate all inputs using functions above
            validate_num('distance')
            validate_datetime('date', '%Y-%m-%d')
            validate_datetime('start_time', '%H:%M:%S')
            validate_datetime('cut_off_time', '%H:%M:%S')
            validate_num('field_limit')           
            validate_num('fee') 

            return func(*args, **kwargs)
        return wrapper
    return decorator

# a route to view all races
@races.route('/',methods = ['GET'])
def get_races():
    # query all races from the database
    races_list = Race.query.all()
    # convert to json format
    result = races_schema.dump(races_list)
    # return the result
    return jsonify(result)

# a route to add a race (admin only)
@races.route('/add',methods = ['POST'])
@jwt_required()
@validate_input(['name', 'distance', 'date', 'start_time', 'cut_off_time', 'field_limit','start_line', 'finish_line', 'fee'])
def add_race():
    # get id of the user
    id = get_jwt_identity()
    participant = Participant.query.get(id)
    # if user is admin, allow to add race
    if participant.admin:
        # get data from the request
        race_fields = race_schema.load(request.json)

        # if race already exists, return error
        race = Race.query.filter_by(name = race_fields['name'], distance=race_fields['distance'], date=race_fields['date']).first()
        if race:
            return abort(400, description = 'Race already exists!')
            
        # if all good, create race object
        race = Race(**race_fields)
        # add race to the database
        db.session.add(race)
        db.session.commit()
        return jsonify(race_schema.dump(race))

    # if not admin, return error message
    return abort(401, description = 'Invalid User')