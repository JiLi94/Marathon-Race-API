from main import db
from flask import Blueprint
from main import bcrypt
from models.participants import Participant
from models.age_groups import Age_group
from models.races import Race
from models.registrations import Registration
from models.results import Result
from datetime import datetime, timedelta

db_commands = Blueprint('db', __name__)

# create app's cli command named create, then run it in the terminal as "flask db create"
@db_commands.cli.command('init')
def init_db():
    db.drop_all()
    db.create_all()
    print('Tables are dropped and recreated')

@db_commands.cli.command('seed')
def seed_db():
    # create one participant instance
    participant1 = Participant(
        # set all attributes of participant
        first_name = 'Eliud',
        last_name = 'Kipchoge',
        email = 'test@test.com',
        mobile = '0412345678',
        password = bcrypt.generate_password_hash('Password12345678').decode('utf-8'),
        date_of_birth = datetime.strptime('1984-11-05', '%Y-%m-%d'),
        gender = 'male',
        admin = True
    )
    # add the instance as a new row into the table
    db.session.add(participant1)

    # seed all age groups into db
    age_groups =[
        [0, 17],
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
        group.min_age = i[0]
        group.max_age = i[1]
        db.session.add(group)

    # create one race instance
    race1 = Race(
        name = 'Berlin Marathon',
        distance = 42.195,
        date = datetime.strptime('2022-09-25', '%Y-%m-%d'),
        start_time = datetime.strptime('07:00:00', '%H:%M:%S'),
        cut_off_time = datetime.strptime('14:00:00', '%H:%M:%S'),
        field_limit = 8500,
        start_line = 'Batman Avenue (150m North of Rod Laver Arena)',
        finish_line = 'Melbourne Cricket Ground (MCG)',
        fee = 160.00
    )
    db.session.add(race1)
    # commit changes before creating instance for registration, because it has foreign keys of previous tables
    db.session.commit()

    # create one registration instance
    registration1 = Registration(
        participant_id = participant1.id,
        race_id = race1.id,
        age_group_id = 3,
        gender_group = participant1.gender,
        # registration date needs to be on or before race date
        registration_date = race1.date,
        bib_number = 'A1234'
    )
    db.session.add(registration1)
    db.session.commit()

    # create one result instance
    result1 = Result(
        finished = True,
        registration_id = registration1.id,
        # start_at should be larger than race start time
        start_at = datetime.strptime('07:00:00', '%H:%M:%S'),
        # if finished, finish_at should be smaller than race cut_off time
        finish_at = datetime.strptime('08:00:00', '%H:%M:%S'),
    )
    result1.finish_time = result1.finish_at - result1.start_at
    result1.pace = result1.finish_time #timedelta(seconds = result1.finish_time.total_seconds()/race1.distance)
    db.session.add(result1)
    db.session.commit()

    print('Table seeded')