from main import db
from flask import Blueprint
from main import bcrypt
from models.participants import Participant
from models.age_groups import Age_group
from datetime import datetime

db_commands = Blueprint('db', __name__)

# create app's cli command named create, then run it in the terminal as "flask db create"
@db_commands.cli.command('create')
def create_db():
    db.create_all()
    print('Tables created successfully')

@db_commands.cli.command('seed')
def seed_db():
    # create the participant instance
    participant1 = Participant(
        # set all attributes of participant
        first_name = 'Eliud',
        last_name = 'Kipchoge',
        email = 'test@test.com',
        mobile = '1234567890',
        password = bcrypt.generate_password_hash('password12345678').decode('utf-8'),
        date_of_birth = datetime.strptime('1984-11-05', '%Y-%m-%d'),
        gender = 'Male',
        admin = False
    )
    # add the instance as a new row into the table
    db.session.add(participant1)

    # seed all age groups into db
    age_groups =[
        [18, 19],
        [20, 39],
        [40, 44],
        [45, 49],
        [50, 54],
        [55, 59],
        [60, 64],
        [65, 69],
        [70, 74],
        [75, None]
    ]
    for i in age_groups:
        group = Age_group()
        group.age_group = i
        db.session.add(group)

    # commit changes
    db.session.commit()
    print('Table seeded')

@db_commands.cli.command('drop')
def drop_db():
    db.drop_all()
    print('Tables dropped')