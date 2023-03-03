from main import db

class Race(db.Model):
    # define the table name
    __tablename__ = 'races'
    # set the primary key
    id = db.Column(db.Integer, primary_key=True)
    # add other columns
    name = db.Column(db.String(), nullable=False)
    distance = db.Column(db.Float(), nullable=False)
    date = db.Column(db.Date(), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    cut_off_time = db.Column(db.DateTime(), nullable=False)
    filed_limit = db.Column(db.Integer(), nullable=False)
    start_line = db.Column(db.String(), nullable=False)
    finish_line = db.Column(db.String(), nullable=False)
    fee = db.Column(db.String(), nullable=False)
    
    