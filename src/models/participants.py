from main import db

class Participant(db.Model):
    # define the table name
    __tablename__ = 'participants'
    # set the primary key
    id = db.Column(db.Integer, primary_key=True)
    # add other columns
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    # email and mobile cannot be duplicated
    email = db.Column(db.String(), nullable=False, unique=True)
    mobile = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    date_of_birth = db.Column(db.Date(), nullable=False)
    gender = db.Column(db.String(), nullable=False)
    admin = db.Column(db.Boolean(), nullable=False, default=False)
    registrations = db.relationship('Registration', backref = 'participant')
