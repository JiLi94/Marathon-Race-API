from main import db

class Registration(db.Model):
    # define table name
    __tablename__ = 'registrations'
    # define primary key
    id = db.Column(db.Integer(), primary_key=True)
    # add foreign keys
    participant_id = db.Column(db.Integer(), db.ForeignKey('participants.id'), nullable=False)
    race_id = db.Column(db.Integer(), db.ForeignKey('races.id'), nullable=False)
    age_group_id = db.Column(db.Integer(), db.ForeignKey('age_groups.id'), nullable=False)
    # add other columns
    # gender_group = db.Column(db.String(), nullable=False)
    registration_date = db.Column(db.Date(), nullable=False)
    bib_number = db.Column(db.String(), nullable=False)
    # add a constraint: the combination of participant id and race id should be unique
    constraint = db.UniqueConstraint(participant_id, race_id)
    constraint = db.UniqueConstraint(bib_number, race_id)
    result = db.relationship(
        'Result',
        backref = 'registration',
        # make sure it's one-to-one relationship
        uselist = False
    )
