from flask import Blueprint, jsonify, request, abort
from main import db
from sqlalchemy import text, exc
from models.results import Result
from models.registrations import Registration
from models.races import Race
from models.age_groups import Age_group
from models.results import Result
from schemas.result_schema import result_schema, results_schema
from validator import is_admin, validate_input
from datetime import datetime, timedelta

results = Blueprint('results', __name__, url_prefix='/results')

# a route to view all results for a given race, age group and gender group
@results.route('/', methods=['GET'])
def get_race_results():
    args = request.args
    race_id = (int(args.get('race_id', False)) or None)
    age_group_id = (int(args.get('age_group_id', False)) or None)
    gender_group = (args.get('gender_group', False).lower() or None)
    # query the database to check existing registrations with same race, age group and gender
    sql = text('SELECT a.* FROM results AS a, registrations AS b\
                WHERE a.registration_id = b.id \
                AND b.race_id = COALESCE(:race_id, b.race_id) \
                AND b.age_group_id = COALESCE(:age_group_id, b.age_group_id) \
                AND b.gender_group = COALESCE(:gender_group, b.gender_group)'
            )
    # execute query and transfer results to a list of dictionaries
    sql_results = db.session.execute(
        sql, {
            # if some values are not passed, consider to query all registrations under that category
            'race_id': race_id,
            'age_group_id': age_group_id,
            'gender_group': gender_group
        }
    ).mappings().all()
    # extract the ids of the results
    results_id = [sql_result['id'] for sql_result in sql_results]
    # get all results by ids
    results_list = Result.query.filter(Result.id.in_(results_id)).order_by(Result.finish_time.desc()).all()
    # get the race and age group
    race = Race.query.get(race_id)
    age_group = Age_group.query.get(age_group_id)
    # add the race, age group, gender and results to the final output
    output = {
        'race': race.name,
        'age_group': {
            'min_age': age_group.min_age,
            'max_age': age_group.max_age
        },
        'gender_group': gender_group,
        'results': results_schema.dump(results_list)
    }
    return jsonify(output)

# def a function to make sure the inputs are meaningful
def validate_results_schema(input):
    registration = Registration.query.get(input['registration_id'])
    if not registration:
        return abort(404, 'Registration not found')
    
    # finish time should be larger than start time
    if input['finish_at'] <= input['start_at']:
        return abort(400, 'Finish time cannot be earlier than start time')
        
    # calculate finish time automatically
    delta = (datetime.strptime(input['finish_at'],'%H:%M:%S') - datetime.strptime(input['start_at'],'%H:%M:%S'))
    input['finish_time'] = str(delta)
    race = Race.query.get(registration.race_id)
    # calculate pace: time used per kilometer
    input['pace'] = (datetime(2000,1,1) + timedelta(seconds=delta.total_seconds()/float(race.distance))).time().strftime('%H:%M:%S')
    return input

# a route to add new result
@results.route('/', methods=['POST'])
@is_admin
# make sure inputs are in valid format
@validate_input(result_schema, ['registration_id','finished','start_at','finish_at'])
def add_result():
    # make sure inputs are meaningful
    input = validate_results_schema(result_schema.load(request.json))
    result = Result(**input)
    db.session.add(result)
    try:
        db.session.commit()
    # if integrity err, means duplicated registration ids found
    except exc.IntegrityError:
        return abort(400, description='Result with same registration id already exists')
    
    return jsonify(description='Added successfully', result = input)

# a route to update existing result
@results.route('/<int:result_id>', methods=['PUT'])
@is_admin
@validate_input(result_schema)
def update_result(result_id):
    input = validate_results_schema(result_schema.load(request.json))
    result = Result.query.get(result_id)

    # update fields
    for key, value in input.items():
        if getattr(result, key) is not None and getattr(result, key) != value:
            setattr(result, key, value)
    try:
        db.session.commit()
    except exc.IntegrityError:
        return abort(400, description='Result with same registration id already exists')

    result = validate_results_schema(result_schema.dump(result))
    db.session.commit()
    return jsonify(msg = 'Updated successfully', result = result_schema.dump(result))
    



