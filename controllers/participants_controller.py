from flask import Blueprint, jsonify, request, abort
from sqlalchemy import exc
from main import db, bcrypt
from models.participants import Participant
from models.registrations import Registration
from schemas.participant_schema import participant_schema, participants_schema
from schemas.registration_schema import registrations_schema
from datetime import  timedelta
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from validator import validate_input, is_admin

participants = Blueprint('participants', __name__, url_prefix='/participants')

@participants.route('/all', methods=['GET'])
@is_admin
def get_participants():
    # query all participants from the database
    participants_list = Participant.query.all()
    # convert the data into a JSON format
    result = participants_schema.dump(participants_list)
    # return the data in JSON format
    return jsonify(result)


# register a new participant
@participants.route('/register', methods=['POST'])
# validate input
@validate_input(participant_schema, ['first_name', 'last_name', 'email', 'mobile', 'password', 'date_of_birth', 'gender'])
def register_participant():
    # import request
    participant_fields = participant_schema.load(request.json)
    participant = Participant(**participant_fields)
    # hash password
    participant.password = bcrypt.generate_password_hash(participant_fields['password']).decode('utf-8')
    # convert gender to lower case
    participant.gender = participant_fields['gender'].lower()
    # default admin to be false
    participant.admin = False
    # add to the database
    db.session.add(participant)
    try:
        db.session.commit()
    # if IntegrityError, means email or mobile is already registered
    except exc.IntegrityError as err:
        return abort(400, description='Participant already registered')

    # create a variable to store token expiration time
    expiry = timedelta(hours=1)
    # create access token
    access_token = create_access_token(
        identity=str(participant.id), expires_delta=expiry)
    # return the user email and access token
    return jsonify({'User': participant.email, 'token': access_token})


# log in
@participants.route('/login', methods=['POST'])
def login():
    # get data from the request
    participant_fields = participant_schema.load(request.json)

    # find the user in the database based on email or mobile
    if 'email' in participant_fields:
        participant = Participant.query.filter_by(
            email=participant_fields['email']).first()
    elif 'mobile' in participant_fields:
        participant = Participant.query.filter_by(
            mobile=participant_fields['mobile']).first()
    else:
        return abort(401, description="Please provide email address or mobile to login")
    # if user is not found or password is incorrect
    if not participant or not bcrypt.check_password_hash(participant.password, participant_fields['password']):
        return abort(401, description="Incorrect login details")

    # create a variable to store token expiration time
    expiry = timedelta(hours=1)
    # create access token
    access_token = create_access_token(
        identity=str(participant.id), expires_delta=expiry)

    # return the user email and access token
    return jsonify({'User': participant.email, 'token': access_token})


# check personal details
@participants.route('/<int:participant_id>', methods=['GET'])
@jwt_required()
def check_personal_details(participant_id):
    # access identity of current participant
    id = get_jwt_identity()
    participant = Participant.query.get(id)
    # if user is trying to access their own details, or the user is admin, allow access
    if int(id) == participant_id or participant.admin:
        result = participant_schema.dump(participant)
        return jsonify(result)
    # otherwise, the participant is not allowed to check other people's details
    return abort(401, description='Invalid User')


# update details
@participants.route('/<int:participant_id>', methods=['PUT'])
@jwt_required()
@validate_input(participant_schema)
def update_personal_details(participant_id):
    # get user input
    input_fields = participant_schema.load(request.json)
    # access identity of current user 
    id = get_jwt_identity()
    user = Participant.query.get(id)
    # access details of the user to be updated
    participant = Participant.query.get(participant_id)

    # if participant not exists, return error
    if not participant:
        return abort(404, description='User not found')
    # if user is admin, or user is trying to update their own details, continue to update
    elif user.admin or user.id == participant.id:
        # else, can continue to update fields
        for key, value in input_fields.items():
            # if user is admin, allow to update the 'admin' field
            if key == 'admin':
                if participant.admin:
                    participant.admin = value
            elif key == 'password':
                participant.password = bcrypt.generate_password_hash(
                    value).decode('utf-8')
            # update other attributes
            elif getattr(participant, key) is not None and getattr(participant, key) != value:
                setattr(participant, key, value)
        try:
            db.session.commit()
        except exc.IntegrityError:
            return abort(400, description='Email or mobile already registered')
        # # convert to json format
        result = participant_schema.dump(participant)
        return jsonify(msg='Updated successfully', Updated=result)
    else:
        return abort(401, 'Invalid User')


# a route to view races under one participant
@participants.route('/<int:participant_id>/registrations', methods=['GET'])
@jwt_required()
def get_races_participant(participant_id):
    id = get_jwt_identity()
    participant = Participant.query.get(id)
    # check if it's a valid participant, if not, return error
    if not participant:
        return abort(404, description='Participant not found')
    # only allow to check the registration if the participant is trying to check their own registration or the user is admin
    if int(id) == participant_id or participant.admin:
        # query all registrations under the participant from the database
        registrations_list = Registration.query.filter_by(
            participant_id=participant_id).all()
        # convert to json format
        result = registrations_schema.dump(registrations_list)
        # return the result
        return jsonify(result)
    # otherwise, the participant is not allowed to check other people's registrations
    return abort(401, description='Invalid User')
