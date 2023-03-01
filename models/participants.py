from main import db

class Participant(db.Model):
    # define the table name
    __tablename__ = 'participants'
    # set the primary key
    id = db.Column(db.Integer, primary_key=True)
    # add other columns
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    mobile = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    date_of_birth = db.Column(db.Date(), nullable=False)
    gender = db.Column(db.String(), nullable=False)
    admin = db.Column(db.Boolean(), nullable=False, default=False)
