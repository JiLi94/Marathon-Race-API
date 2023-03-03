from flask import Blueprint, jsonify, request, abort
from sqlalchemy import or_
from main import db, bcrypt, jwt
from models.participants import Participant
from schemas.participant_schema import participant_schema, participants_schema
from email_validator import validate_email, EmailNotValidError
from phonenumbers import parse, is_valid_number
from password_strength import PasswordPolicy
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, jwt_required

participants = Blueprint('participants', __name__, url_prefix='/participants')

# define a decorator to validate format of user details, such as name and email format
def validate_input(func):
    def wrapper():
        participant_fields = participant_schema.load(request.json)
        # validate name
        if not (participant_fields['first_name'].isalpha() and participant_fields['last_name'].isalpha()):
            return abort(400, description='Please enter valid first and last name')
        
        # validate email
        try:
            email = validate_email(participant_fields['email'])
        except EmailNotValidError:
            return abort(400, description='Please enter a valid email address')

        # validate mobile number
        try:
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
        if password_policy.test(participant_fields['password']):
            return abort(400, description='The password must be at least 8 letters long and have at least 1 uppercase letter')

        # validate date of birth format
        try:
            dob = datetime.strptime(
                participant_fields['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return abort(400, description='Please enter a valid date for date_of_birth in the format of yyyy-MM-dd')

        # validate gender format
        if participant_fields['gender'].lower() not in ['male', 'female']:
            return abort(400, description='Please select male or female for gender')
            
        return func()
 
    return wrapper


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
@validate_input
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
    #create access token
    access_token = create_access_token(identity = str(participant.id), expires_delta=expiry)
    # return the user email and access token
    return jsonify({'User':participant.email, 'token': access_token})


# log in
@participants.route('/login', methods=['POST'])
def login():
    # get data from the request
    participant_fields = participant_schema.load(request.json)

    # find the user in the database based on email or mobile
    if 'email' in participant_fields:
        participant = Participant.query.filter_by(email = participant_fields['email']).first()
    elif 'mobile' in participant_fields:
        participant = Participant.query.filter_by(mobile = participant_fields['mobile']).first()
    else:
        return abort(401, description="Please enter email address or mobile to login")
    # if user is not found or password is incorrect
    if not participant or not bcrypt.check_password_hash(participant.password, participant_fields['password']):
        return abort(401, description="Incorrect login detail")
    
    # create a variable to store token expiration time
    expiry = timedelta(hours=1)
    #create access token
    access_token = create_access_token(identity = str(participant.id), expires_delta=expiry)
    # return the user email and access token
    return jsonify({'User':participant.email, 'token': access_token})


# update details
# @participants.route('/update', methods=['PUT'])
# @jwt_required
# def update_details():


# a route to view races under one participant
@participants.route('/<int:participant_id>', methods = ['GET'])
# @jwt_required
def get_races_participant(participant_id):
    # query all registrations under the participant from the database
    registrations_list = Registration.query.filter_by(participant_id=participant_id).all()
    # convert to json format
    result = registrations_schema.dump(registrations_list)
    # return the result
    return jsonify(result)