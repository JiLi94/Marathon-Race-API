from flask import Blueprint, jsonify, request, abort
from sqlalchemy import or_
from main import db, bcrypt
from models.participants import Participant
from schemas.participant_schema import participant_schema, participants_schema

participants = Blueprint('participants', __name__, url_prefix='/participants')


# get all participants from the database
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
def register_participant():
    # import request
    participant_fields = participant_schema.load(request.json)
    # check if user is already registered, check both email and mobile
    participant = Participant.query.filter(or_(
        Participant.email == participant_fields['email'], Participant.mobile == participant_fields['mobile'])).first()
    # participant = Participant.query.filter_by(email=participant_fields['email']).first()
    # if participant is already registered, return error message
    if participant:
        return abort(400, description='Participant already registered')
    # otherwise, create participant object
    participant = Participant(**participant_fields)
    participant.password = bcrypt.generate_password_hash(
        participant_fields['password']).decode('utf-8')
    # add to the database
    db.session.add(participant)
    db.session.commit()
    return jsonify(participant_schema.dump(participant))
