from flask import Blueprint, jsonify, request, abort
from sqlalchemy import and_
from sqlalchemy.sql.functions import coalesce
from main import db, bcrypt, jwt
from models.registrations import Registration
from models.participants import Participant
from models.races import Race
from models.age_groups import Age_group
from controllers.participants_controller import is_admin
from schemas.registration_schema import registration_schema, registrations_schema
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask_jwt_extended import get_jwt_identity, jwt_required
from functools import wraps
from validator import validate_input, is_admin

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
    registration_fields = registration_schema.load(request.json)
    # return jsonify(description='ok')
    # check if participant exists
    participant = Participant.query.get(registration_fields['participant_id'])
    if not participant:
        return abort(404, description='Participant not found')

    # check if race exists
    race = Race.query.get(registration_fields['race_id'])
    if not race:
        return abort(404, description='Race not found')

    # check if the registration already exists
    existing_registration = Registration.query.filter_by(
        participant_id=registration_fields['participant_id'], race_id=registration_fields['race_id']).first()
    if existing_registration:
        return abort(400, description='The registration already exists')
    
    # check if bib number exists
    existing_bib = Registration.query.filter_by(
        bib_number=registration_fields['bib_number']).first()
    if existing_bib:
        return abort(400, description='Bib number already exists')

    registration = Registration(**registration_fields)
    # automatically assign age group based on participant's age on the race date
    # age = (race.date - participant.date_of_birth).days()/365
    age = relativedelta(race.date, participant.date_of_birth).years
    print(race.date, participant.date_of_birth, age)
    # registration.age_group_id = Age_group.query.filter(
    #     age.between(Age_group.min_age, Age_group.max_age)).first()
    registration.age_group_id = Age_group.query.filter(and_(age<=coalesce(Age_group.max_age, age), age>=Age_group.min_age)).first().id
    # automatically assign gender group based on participant's gender
    registration.gender_group = 'male' if participant.gender == 'male' else 'female'
    # add to the database
    db.session.add(registration)
    db.session.commit()
    return jsonify(registration_schema.dump(registration))


# a route to view all participants under a race

# register
# need to check if the participant is already registered, can automatically assign gender and age group
# check if field limit is exceeded
