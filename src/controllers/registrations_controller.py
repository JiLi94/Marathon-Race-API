from flask import Blueprint, jsonify, request, abort
from sqlalchemy import and_, exc
from sqlalchemy.sql.functions import coalesce
from main import db
from models.registrations import Registration
from models.participants import Participant
from models.races import Race
from models.age_groups import Age_group
from controllers.participants_controller import is_admin
from schemas.registration_schema import registration_schema, registrations_schema
from dateutil.relativedelta import relativedelta
from validator import validate_input, is_admin
from parse import parse

registrations = Blueprint('registrations', __name__, url_prefix='/registrations')


# a route to view all registrations, should be admin only
@registrations.route('/', methods=['GET'])
@is_admin
def get_registrations():
    # query all registrations from the database
    registrations_list = Registration.query.all()
    # convert to json format
    result = registrations_schema.dump(registrations_list)
    # return the result
    return jsonify(result)


# add registration
@registrations.route('/', methods=['POST'])
@is_admin
@validate_input(registration_schema, ['participant_id','race_id','registration_date','bib_number'])
def add_registration():
    input = registration_schema.load(request.json)
    # check if participant exists
    participant = Participant.query.get(input['participant_id'])
    if not participant:
        return abort(404, description='Participant not found')

    # check if race exists
    race = Race.query.get(input['race_id'])
    if not race:
        return abort(404, description='Race not found')

    # automatically assign age group based on participant's age on the race date
    age = relativedelta(race.date, participant.date_of_birth).years
    input['age_group_id'] = Age_group.query.filter(and_(age<=coalesce(Age_group.max_age, age), age>=Age_group.min_age)).first().id
    
    # add to the database
    registration = Registration(**input)
    db.session.add(registration)
    try:
        db.session.commit()
    # if IntegrityError, means duplicate registration or bib_number
    except exc.IntegrityError as e:
        # parse the error field, there are two scenarios: duplicated bib_number or participant
        err_field = parse('duplicate key value violates unique constraint "{constraint}"\nDETAIL:  Key ({field})=({input}) already exists.\n', str(e.orig))["field"]
        if err_field == 'bib_number, race_id':
            err_msg = 'Bib number already exists under this race'
        else:
            err_msg = 'Participant already registered this race'
        return abort(400, description = err_msg)
    
    return jsonify(msg = 'Registration added successfully', registration = registration_schema.dump(registration))


# a route to update existing registration
@registrations.route('/<int:id>', methods=['PUT'])
@is_admin
@validate_input(registration_schema)
def update_registration(id):
    registration = Registration.query.get(id)
    input = registration_schema.load(request.json)
    # update fields
    if registration:
        for key, value in input.items():
            if getattr(registration, key) is not None and getattr(registration, key) != value:
                setattr(registration, key, value)
    else:
        return abort(404, description = 'Registration not found')
    
    # check if participant exists
    participant = Participant.query.get(registration.participant_id)
    if not participant:
        return abort(404, description='Participant not found')

    # check if race exists
    race = Race.query.get(registration.race_id)
    if not race:
        return abort(404, description='Race not found')

    try:
        db.session.commit()
    # if IntegrityError, means duplicate registration or bib_number
    except exc.IntegrityError as e:
        # parse the error field, there are two scenarios: duplicated bib_number or participant
        err_field = parse('duplicate key value violates unique constraint "{constraint}"\nDETAIL:  Key ({field})=({input}) already exists.\n', str(e.orig))["field"]
        if err_field == 'bib_number, race_id':
            err_msg = 'Bib number already exists under this race'
        else:
            err_msg = 'Participant already registered this race'
        return abort(400, description = err_msg)
    
    return jsonify(msg = 'Updated successfully', registration = registration_schema.dump(registration))


# a route to delete registration
@registrations.route('/<int:id>', methods = ['DELETE'])
@is_admin
def delete_registration(id):
    registration = Registration.query.get(id)
    registration_serialized = registration_schema.dump(registration)
    if registration:
        try:
            db.session.delete(registration)
            db.session.commit()    
            return jsonify(msg = 'Registration deleted successfully', result = registration_serialized)
        except exc.IntegrityError:
            return abort(400, description='Please delete the result linked with this registration before deleting this registration')
    return abort(404, description = 'Registration not found')

