from flask import Blueprint, jsonify, request, abort
from sqlalchemy import or_
from main import db, bcrypt, jwt
from models.participants import Participant
from schemas.participant_schema import participant_schema, participants_schema
from email_validator import validate_email, EmailNotValidError
from phonenumbers import parse, is_valid_number
from password_strength import PasswordPolicy
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from functools import wraps

participants = Blueprint('participants', __name__, url_prefix='/participants')

# define a decorator to validate format of user details, such as name and email format
# also to valid if the user has input enough information


def validate_input(*args):
    def decorator(func):
        @wraps(func)
        def wrapper():
            participant_fields = participant_schema.load(request.json)
            # check if the user input enough information
            for arg in args:
                if arg not in participant_fields:
                    return abort(400, description='Not enough information provided')
            # validate name
            if 'first_name' in participant_fields and 'last_name' in participant_fields:
                if not (participant_fields['first_name'].isalpha() and participant_fields['last_name'].isalpha()):
                    return abort(400, description='Please enter valid first and last name')

            # validate email
            try:
                if 'email' in participant_fields:
                    email = validate_email(participant_fields['email'])
            except EmailNotValidError:
                return abort(400, description='Please enter a valid email address')

            # validate mobile number
            try:
                if 'mobile' in participant_fields:
                    mobile = parse(participant_fields['mobile'], 'AU')
                    if not is_valid_number(mobile):
                        return abort(400, description='Please enter a valid Australia mobile number or add country code in front of the number')
            except:
                return abort(400, description='Please enter a valid Australia mobile number or add country code in front of the number')

            # validate password
            password_policy = PasswordPolicy.from_names(
                length=8,  # minimum length 8
                uppercase=1,  # minimum 1 uppercase letter
            )
            if 'password' in participant_fields:
                if password_policy.test(participant_fields['password']):
                    return abort(400, description='The password must be at least 8 letters long and have at least 1 uppercase letter')

            # validate date of birth format
            try:
                if 'date_of_birth' in participant_fields:
                    dob = datetime.strptime(
                        participant_fields['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return abort(400, description='Please enter a valid date for date_of_birth in the format of yyyy-MM-dd')

            # validate gender format
            if 'gender' in participant_fields:
                if participant_fields['gender'].lower() not in ['male', 'female']:
                    return abort(400, description='Please select male or female for gender')

            # validate admin format (should be either True or False)
            if 'admin' in participant_fields:
                if not isinstance(participant_fields['admin'], bool):
                    return abort(400, description='Please select True or False for admin')

            return func()
        return wrapper
    return decorator

# def check_existing_user():
#     def wrapper():
#         participant_fields = participant_schema.load(request.json)
#         # check if user is already registered, check both email and mobile
#         participant = Participant.query.filter(or_(
#             Participant.email == participant_fields['email'], Participant.mobile == participant_fields['mobile'])).first()
#         # if participant is already registered, return error message
#         if participant:
#             return abort(400, description='Email or mobile already registered')

# get all participants from the database, admin only


@participants.route('/', methods=['GET'])
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
@validate_input('first_name', 'last_name', 'email', 'mobile', 'password', 'date_of_birth', 'gender')
def register_participant():
    # import request
    participant_fields = participant_schema.load(request.json)

    # check if user is already registered, check both email and mobile
    participant = Participant.query.filter(or_(
        Participant.email == participant_fields['email'], Participant.mobile == participant_fields['mobile'])).first()
    # if participant is already registered, return error message
    if participant:
        return abort(400, description='Participant already registered')

    # if all good, create participant object
    participant = Participant(**participant_fields)
    participant.password = bcrypt.generate_password_hash(
        participant_fields['password']).decode('utf-8')
    participant.gender = participant_fields['gender'].lower()

    # add to the database
    db.session.add(participant)
    db.session.commit()

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
        return abort(401, description="Please enter email address or mobile to login")
    # if user is not found or password is incorrect
    if not participant or not bcrypt.check_password_hash(participant.password, participant_fields['password']):
        return abort(401, description="Incorrect login detail")

    # create a variable to store token expiration time
    expiry = timedelta(hours=1)
    # create access token
    access_token = create_access_token(
        identity=str(participant.id), expires_delta=expiry)
    # return the user email and access token
    return jsonify({'User': participant.email, 'token': access_token})


# update details
@participants.route('/update', methods=['PUT'])
@jwt_required()
@validate_input()
def update_personal_details():
    # get user input
    input_fields = participant_schema.load(request.json)
    # access identity of current participant
    id = get_jwt_identity()
    participant = Participant.query.get(id)
    # check if it's a valid participant, if not, return error
    if not participant:
        return abort(404, description='Participant not found')

    # check if email or mobile is used by other participants
    other_participant = Participant.query.filter(or_(
        Participant.email == input_fields['email'], Participant.mobile == input_fields['mobile'])).first()
    # if yes, return error
    if (other_participant is not None) and (other_participant.id != int(id)):
        return abort(400, description='Email or mobile already registered by another participant')

    for key, value in input_fields.items():
        # cannot update primary key id
        if key == 'id':
            continue
        # if user is admin, can update the 'admin' field
        elif key == 'admin':
            if participant.admin:
                participant.admin = value
        elif key == 'password':
            participant.password = bcrypt.generate_password_hash(
                value).decode('utf-8')
        # update other attributes
        elif getattr(participant, key) is not None and getattr(participant, key) != value:
            setattr(participant, key, value)
    # participant.first_name = input_fields['first_name']
    db.session.commit()
    # # convert to json format
    result = participant_schema.dump(participant)
    return jsonify(msg='Updated successfully', Updated = result)


# a route to view races under one participant
# @participants.route('/<int:participant_id>', methods = ['GET'])
# # @jwt_required
# def get_races_participant(participant_id):
#     # query all registrations under the participant from the database
#     registrations_list = Registration.query.filter_by(participant_id=participant_id).all()
#     # convert to json format
#     result = registrations_schema.dump(registrations_list)
#     # return the result
#     return jsonify(result)
