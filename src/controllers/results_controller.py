from flask import Blueprint, jsonify, request, abort
from main import db
from sqlalchemy import text, exc
from models.results import Result
from models.registrations import Registration
from models.races import Race
from models.age_groups import Age_group
from models.results import Result
from schemas.result_schema import result_schema
from validator import is_admin, validate_input
from datetime import datetime, timedelta

results = Blueprint('results', __name__, url_prefix='/results')

# a route to view all results for a given race, age group and gender group


@results.route('/', methods=['GET'])
def get_race_results():
    args = request.args
    # find the race
    race_id = (int(args.get('race_id', False)) or None)
    race = Race.query.get(race_id)
    if race_id and not race:
        return abort(404, 'Race not found')
    # get the age group
    age_group_id = (int(args.get('age_group_id', False)) or None)
    age_group = Age_group.query.get(age_group_id)
    if age_group_id and not age_group:
        return abort(404, 'Age group not found')
    gender = (args.get('gender', False) or None)
    # query the database to check existing registrations with same race, age group and gender
    sql = text('SELECT first_name, last_name, res.*, \
                ROW_NUMBER () OVER (ORDER BY res.pace ASC) AS row_num \
                FROM results AS res \
                INNER JOIN registrations AS reg ON res.registration_id = reg.id \
                INNER JOIN participants AS par ON par.id = reg.participant_id \
                WHERE reg.race_id = COALESCE(:race_id, reg.race_id) \
                AND reg.age_group_id = COALESCE(:age_group_id, reg.age_group_id) \
                AND par.gender = COALESCE(:gender, par.gender)'
               )
    # execute the query
    sql_results = db.session.execute(
        sql, {
            # if some values are not passed, consider to query all registrations under that category
            'race_id': race_id,
            'age_group_id': age_group_id,
            'gender': gender
        })
    # extract the result into a list
    results_list = []
    for row in sql_results:
        result = {
            'place': row.row_num,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'finished': row.finished,
            'start_at': str(row.start_at),
            'finish_at': str(row.finish_at),
            'finish_time': str(row.finish_time),
            'pace': str(row.pace)
        }
        results_list.append(result)
    # Close the result set explicitly
    sql_results.close()

    # add race, age group and gender into the result
    output = {
        'race': race.name if hasattr(race, 'name') else 'All',
        'age_group': {
            'min_age': age_group.min_age if hasattr(age_group, 'min_age') else 'All',
            'max_age': age_group.max_age if hasattr(age_group, 'max_age') else 'All'
        },
        'gender': gender or 'All',
        'results': results_list
    }
    return jsonify(output)


# def a function to make sure the inputs are meaningful
def validate_results_schema(input):
    registration = Registration.query.get(input['registration_id'])
    if not registration:
        return abort(404, description='Registration not found')
    # finish time should be larger than start time
    if datetime.strptime(input['finish_at'], '%H:%M:%S') <= datetime.strptime(input['start_at'], '%H:%M:%S'):
        return abort(400, 'Finish time cannot be earlier than start time')

    # calculate finish time automatically
    delta = (datetime.strptime(
        input['finish_at'], '%H:%M:%S') - datetime.strptime(input['start_at'], '%H:%M:%S'))
    input['finish_time'] = str(delta)
    # calculate pace: time used per kilometer
    race = Race.query.get(registration.race_id)
    input['pace'] = (datetime(2000, 1, 1) + timedelta(seconds=delta.total_seconds() /
                     float(race.distance))).time().strftime('%H:%M:%S')
    return input


# a route to add new result
@results.route('/', methods=['POST'])
@is_admin
# make sure inputs are in valid format
@validate_input(result_schema, ['registration_id', 'finished', 'start_at', 'finish_at'])
def add_result():
    # get input
    input = validate_results_schema(result_schema.load(request.json))
    registration = Registration.query.get(input['registration_id'])
    if not registration:
        return abort(404, description='Registration not found')
    # finish time should be larger than start time
    if datetime.strptime(input['finish_at'], '%H:%M:%S') <= datetime.strptime(input['start_at'], '%H:%M:%S'):
        return abort(400, 'Finish time cannot be earlier than start time')

    # calculate finish time automatically
    delta = (datetime.strptime(
        input['finish_at'], '%H:%M:%S') - datetime.strptime(input['start_at'], '%H:%M:%S'))
    input['finish_time'] = str(delta)
    # calculate pace: time used per kilometer
    race = Race.query.get(registration.race_id)
    input['pace'] = (datetime(2000, 1, 1) + timedelta(seconds=delta.total_seconds() /
                     float(race.distance))).time().strftime('%H:%M:%S')

    # add to database
    result = Result(**input)
    db.session.add(result)
    try:
        db.session.commit()
    # if integrity err, means duplicated registration ids found
    except exc.IntegrityError:
        return abort(400, description='Result with same registration id already exists')

    return jsonify(description='Added successfully', result=result_schema.dump(result))


# a route to update existing result
@results.route('/<int:result_id>', methods=['PUT'])
@is_admin
@validate_input(result_schema)
def update_result(result_id):
    input = result_schema.load(request.json)
    result = Result.query.get(result_id)

    # update fields
    if result:
        for key, value in input.items():
            if getattr(result, key) is not None and getattr(result, key) != value:
                setattr(result, key, value)
    else:
        return abort(404, description='Result not found')

    # find registration
    registration = Registration.query.get(result.registration_id)
    if not registration:
        return abort(404, description='Registration not found')

    # finish time should be larger than start time
    if datetime.strptime(result.finish_at, '%H:%M:%S') <= datetime.strptime(result.start_at, '%H:%M:%S'):
        return abort(400, 'Finish time cannot be earlier than start time')

    # calculate finish time automatically
    delta = (datetime.strptime(result.finish_at, '%H:%M:%S') -
             datetime.strptime(result.start_at, '%H:%M:%S'))
    result.finish_time = str(delta)
    # calculate pace: time used per kilometer
    race = Race.query.get(registration.race_id)
    result.pace = (datetime(2000, 1, 1) + timedelta(seconds=delta.total_seconds() /
                   float(race.distance))).time().strftime('%H:%M:%S')

    # update database
    try:
        db.session.commit()
    # if IntegrityError, means duplicated registrations
    except exc.IntegrityError:
        return abort(400, description='Result with same registration id already exists')
    return jsonify(msg='Updated successfully', result=result_schema.dump(result))


# a route to delete an existing result
@results.route('/<int:result_id>', methods=['DELETE'])
@is_admin
def delete_result(result_id):
    result = Result.query.get(result_id)
    result_serialized = result_schema.dump(result)
    if result:
        db.session.delete(result)
        db.session.commit()
        return jsonify(msg='Result deleted successfully', result=result_serialized)
    # if result not exists
    return abort(404, description='Result not found')
