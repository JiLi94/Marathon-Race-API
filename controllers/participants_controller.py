from flask import Blueprint, jsonify, request
from main import db
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
