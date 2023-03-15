from flask import Blueprint, jsonify, request, abort
from main import db
from models.races import Race
from controllers.participants_controller import is_admin
from schemas.race_schema import race_schema, races_schema
from sqlalchemy import text, exc
from validator import validate_input, is_admin

races = Blueprint('races', __name__, url_prefix='/races')

# a route to view all races
@races.route('/', methods=['GET'])
def get_races():
    # query all races from the database
    races_list = Race.query.all()
    # convert to json format & return the result
    return jsonify(races_schema.dump(races_list))

# a route to check one single race
@races.route('/<int:id>', methods=['GET'])
def get_race(id):
    # query race from the database
    race = Race.query.get(id)
    # convert to json format and return the result
    return jsonify(race_schema.dump(race))

# a route to add a race (admin only)
@races.route('/', methods=['POST'])
@is_admin
@validate_input(race_schema, ['name', 'distance', 'date', 'start_time', 'cut_off_time', 'field_limit', 'start_line', 'finish_line', 'fee'])
def add_race():
    # get data from the request
    race_fields = race_schema.load(request.json)
    race = Race(**race_fields)
    # add race to the database
    db.session.add(race)
    try:
        db.session.commit()
    except exc.IntegrityError:
        return abort(400, description='Race already exists!')
    return jsonify(race_schema.dump(race))

# a route to update a race (admin only)
@races.route('/<int:race_id>', methods=['PUT'])
@validate_input(race_schema)
@is_admin
def update_race(race_id):
    # get user input
    input_fields = race_schema.load(request.json)
    race = Race.query.get(race_id)

    # update fields
    for key, value in input_fields.items():
        if getattr(race, key) is not None and getattr(race, key) != value:
            setattr(race, key, value)

    try:
        db.session.commit()
    except exc.IntegrityError:
        return abort(400, description='Race already exists!')
    # # convert to json format
    result = race_schema.dump(race)
    return jsonify(msg='Updated successfully', Updated=result)

# a route to delete a race
@races.route('/<int:id>', methods=['DELETE'])
@is_admin
def delete_registration(id):
    race = Race.query.get(id)
    race_serialized = race_schema.dump(race)
    if race:
        try:
            db.session.delete(race)
            db.session.commit()    
            return jsonify(msg = 'Race deleted successfully', result = race_serialized)
        except exc.IntegrityError:
            return abort(400, description='Please delete the registrations linked with this race before deleting this race')
    return abort(404, description = 'Race not found')
