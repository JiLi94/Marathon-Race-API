from main import db

class Age_group(db.Model):
    #define table_name
    __tablename__ = 'age_groups'
    # define primary key
    id = db.Column(db.Integer(), primary_key=True)
    # add other column
    age_group = db.Column(db.String(), nullable=False)
    registrations = db.relationship(
        'Registration',
        backref = 'age_group',
        cascade = 'all, delete'
    )