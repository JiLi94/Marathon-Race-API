from flask import Blueprint, jsonify, request, abort
from main import db
from sqlalchemy import text
from models.results import Result
from models.registrations import Registration
from schemas.result_schema import result_schema, results_schema
from schemas.registration_schema import registrations_schema

results = Blueprint('results', __name__, url_prefix='/results')

# a route to view all results for a given race, age group and gender group
@results.route('/', methods=['GET'])
def get_race_results():
    args = request.args

    # query the database to check existing registrations with same race, age group and gender
    sql = text('SELECT a.* FROM results AS a, registrations AS b\
                WHERE a.registration_id = b.id \
                AND b.race_id = COALESCE(:race_id, b.race_id) \
                AND b.age_group_id = COALESCE(:age_group_id, b.age_group_id) \
                AND b.gender_group = COALESCE(:gender_group, b.gender_group)'
            )
    # execute query and transfer results to a list of dictionaries
    results_id = db.session.execute(
        sql, {
            # if some values are not passed, consider to query all registrations under that category
            'race_id': (int(args.get('race_id', False)) or None),
            'age_group_id': (int(args.get('age_group_id', False)) or None),
            'gender_group': (int(args.get('gender_group', False)) or None)
        }
    ).mappings().all()
    # extract the ids of the results
    results_id = [result_id['id'] for result_id in results_id]
    # get the list of results by ids
    results_list = Result.query.filter(Result.id.in_(results_id)).all()
    # return the dumped results
    return jsonify(results_schema.dump(results_list))
