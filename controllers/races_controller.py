from flask import Blueprint, jsonify, request, abort
from main import db, bcrypt, jwt
from models.races import Race
from schemas.race_schema import race_schema, races_schema
from datetime import datetime, timedelta

races = Blueprint('races', __name__, url_prefix='/races')

# a route to view all races
@races.route('/',methods = ['GET'])
def get_races():
    # query all races from the database
    races_list = Race.query.all()
    # convert to json format
    result = races_schema.dump(races_list)
    # return the result
    return jsonify(result)

