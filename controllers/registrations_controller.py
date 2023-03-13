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
import json

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

# # def a func to make sure inputs are meaningful
# def validate_registration_schema(input):
#     # check if participant exists
#     participant = Participant.query.get(input['participant_id'])
#     if not participant:
#         return abort(404, description='Participant not found')

#     # check if race exists
#     race = Race.query.get(input['race_id'])
#     if not race:
#         return abort(404, description='Race not found')

#     # check if bib number exists
#     existing_bib = Registration.query.filter_by(
#         bib_number=input['bib_number'], race_id=input['race_id']).first()
#     if existing_bib:
#         return abort(400, description='Bib number already exists')

#     # automatically assign age group based on participant's age on the race date
#     age = relativedelta(race.date, participant.date_of_birth).years
#     input['age_group_id'] = Age_group.query.filter(and_(age<=coalesce(Age_group.max_age, age), age>=Age_group.min_age)).first().id
#     # automatically assign gender group based on participant's gender
#     input['gender_group'] = 'male' if participant.gender == 'male' else 'female'
#     return input

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

    # check if bib number exists
    # existing_bib = Registration.query.filter_by(
    #     bib_number=input['bib_number'], race_id=input['race_id']).first()
    # if existing_bib:
    #     return abort(400, description='Bib number already exists')

    # automatically assign age group based on participant's age on the race date
    age = relativedelta(race.date, participant.date_of_birth).years
    input['age_group_id'] = Age_group.query.filter(and_(age<=coalesce(Age_group.max_age, age), age>=Age_group.min_age)).first().id
    # automatically assign gender group based on participant's gender
    input['gender_group'] = 'male' if participant.gender == 'male' else 'female'
    # add to the database
    registration = Registration(**input)
    db.session.add(registration)
    try:
        db.session.commit()
    # if IntegrityError, means duplicate registration
    except exc.IntegrityError:
        return abort(400, description='Registration or bib number already exists')
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

    # check if bib number exists
    # existing_bib = Registration.query.filter_by(
    #     bib_number=registration.bib_number, race_id=registration.race_id).first()
    # if existing_bib and existing_bib.id != registration.id:
    #     return abort(400, description='Bib number already exists')  

    try:
        db.session.commit()
    except exc.IntegrityError:
        return abort(400, description='Registration or bib number already exists')
    
    return jsonify(msg = 'Updated successfully', registration = registration_schema.dump(registration))
# a route to delete registration
# @registrations.route('/<int:registration_id>', methods=['PUT'])
# @is_admin
# @validate_input(registration_schema)
# def update_registration(registration_id):
#     input_fields = registration_schema.load(request.json)
#     registration = Registration.query.get(registration_id)
#     if not registration:
#         return abort(404, description='Registration not found')
    

