from flask import abort, request
from email_validator import validate_email, EmailNotValidError
from phonenumbers import parse, is_valid_number
from password_strength import PasswordPolicy
from datetime import datetime, timedelta
from functools import wraps
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.participants import Participant

class Validator():

    def __init__(self, data):
        self.data = data

    # def a function to validate number
    def validate_number(self, field, min, max=None):
        try:
            if (min is not None and float(self.data[field]) < min) or (max is not None and float(self.data[field]) > max):
                return abort(400, description=f'Please enter a valid number for {field} between [{min}, {max}]')
        except ValueError:
            return abort(400, description=f'Please enter a valid number for {field} between [{min}, {max}]')

    # def a function to validate date or time input
    def validate_datetime(self, field, datetime_format):
        try:
            date_time = datetime.strptime(self.data[field], datetime_format)
            if field == 'date_of_birth' and date_time > date_time.now():
                return abort(400, description=f'Please enter a valid date for {field} in the format of {datetime_format}')
        except ValueError:
            return abort(400, description=f'Please enter a valid date for {field} in the format of {datetime_format}')
    
    # validate person name fields
    def validate_name(self, field):
        if not self.data[field].replace(' ','').isalpha():
            return abort(400, description=f'Please enter valid {field}')
    
    # validate string fields
    def validate_string(self, field):
        if not isinstance(self.data[field], str):
            return abort(400, description=f'Please enter valid {field}')

    # validate email
    def validate_emails(self):
        try:
            email = validate_email(self.data['email'])
        except EmailNotValidError:
            return abort(400, description='Please enter a valid email address')

    # validate mobile number
    def validate_mobile(self):
        try:
            mobile = parse(self.data['mobile'], 'AU')
            if not is_valid_number(mobile):
                return abort(400, description='Please enter a valid Australia mobile number or add country code in front of the number')
        except:
            return abort(400, description='Please enter a valid Australia mobile number or add country code in front of the number')

    # validate password
    def validate_password(self):
        password_policy = PasswordPolicy.from_names(
            length=8,  # minimum length 8
            uppercase=1,  # minimum 1 uppercase letter
        )
        if password_policy.test(self.data['password']):
            return abort(400, description='The password must be at least 8 letters long and have at least 1 uppercase letter')

    # validate gender format
    def validate_gender(self):
        if self.data['gender'].lower() not in ['male', 'female']:
            return abort(400, description='Please select male or female for gender')

    # validate boolean format (should be either True or False)
    def validate_boolean(self, field):
        if not isinstance(self.data[field], bool):
            return abort(400, description=f'Please select True or False for {field}')
        

# define a decorator to validate format of user details, such as name and email format
# also to valid if the user has input enough information
def validate_input(schema, required_fields=[]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            input_fields = schema.load(request.json)
            # check if the user inputs enough information
            missing_fields = []
            for field in required_fields:
                if field not in input_fields:
                    missing_fields.append(field)
            # if missing fields, return error and ask for more information
            if missing_fields:
                return abort(400, description=f'Please provide {", ".join(field for field in missing_fields)}')

            validator = Validator(input_fields)
            for field in input_fields:
                match field:
                    case 'name'|'start_line'|'finish_line'|'bib_number':
                        validator.validate_string(field)
                    case 'first_name'|'last_name':
                        validator.validate_name(field)
                    case 'email':
                        validator.validate_emails()
                    case 'mobile':
                        validator.validate_mobile()
                    case 'password':
                        validator.validate_password()
                    case 'date_of_birth'|'date'|'registration_date':
                        validator.validate_datetime(field, '%Y-%m-%d')
                    case 'gender':
                        validator.validate_gender()
                    case 'admin'|'finished':
                        validator.validate_boolean(field)
                    case 'distance'|'fee'|'field_limit'|'participant_id'|'race_id'|'registration_id':
                        validator.validate_number(field, 0)
                    case 'start_time'|'end_time'|'start_at'|'finish_at':
                        validator.validate_datetime(field, '%H:%M:%S')

            return func(*args, **kwargs)
        return wrapper
    return decorator

def is_admin(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        id = get_jwt_identity()
        participant = Participant.query.get(id)
        if not participant or not participant.admin:
            return abort(401, description='Invalid User')

        return func(*args, **kwargs)
    return wrapper