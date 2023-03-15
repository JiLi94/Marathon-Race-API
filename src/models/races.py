from main import db

class Race(db.Model):
    # define the table name
    __tablename__ = 'races'
    # set the primary key
    id = db.Column(db.Integer, primary_key=True)
    # add other columns
    name = db.Column(db.String(), nullable=False)
    distance = db.Column(db.Numeric(10,2), nullable=False)
    date = db.Column(db.Date(), nullable=False)
    start_time = db.Column(db.Time(), nullable=False)
    cut_off_time = db.Column(db.Time(), nullable=False)
    field_limit = db.Column(db.Integer(), nullable=False)
    start_line = db.Column(db.String(), nullable=False)
    finish_line = db.Column(db.String(), nullable=False)
    fee = db.Column(db.Numeric(10,2), nullable=False)
    constraint = db.UniqueConstraint(name, date)
    registrations = db.relationship(
        'Registration',
        backref = 'race',
        # cascade = 'all, delete'
    )
    