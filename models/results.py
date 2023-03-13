from main import db

class Result(db.Model):
    # define table name
    __tablename__ = 'results'
    # add primary key
    id = db.Column(db.Integer(), primary_key=True)
    # add foreign key
    registration_id = db.Column(db.Integer(), db.ForeignKey('registrations.id'), nullable=False, unique=True)
    # add other columns
    finished = db.Column(db.Boolean(), nullable=False)
    # the timestamp when started and finished
    start_at = db.Column(db.Time(), nullable=False)
    finish_at = db.Column(db.Time(), nullable=False)
    # time used to finish the race
    finish_time = db.Column(db.Time(), nullable=False)
    # average pace per km
    pace = db.Column(db.Time(), nullable=False)
    registration = db.relationship('Registration', backref = 'registration')
