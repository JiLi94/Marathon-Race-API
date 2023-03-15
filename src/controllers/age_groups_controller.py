from flask import Blueprint, jsonify, request, abort
from models.age_groups import Age_group
from schemas.age_group_schema import age_groups_schema


age_groups = Blueprint('age_groups', __name__, url_prefix='/age_groups')

# a route to view all age_groups
@age_groups.route('/', methods = ['GET'])
def get_races():
    # query all registrations from the database
    age_groups_list = age_groups.query.all()
    # convert to json format
    result = age_groups_schema.dump(age_groups_list)
    # return the result
    return jsonify(result)

