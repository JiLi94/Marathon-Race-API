from main import ma
from marshmallow import fields


class RegistrationSchema(ma.Schema):
    class Meta:
        # fields to output
        fields = ('participant', 'race', 'age_group',
                  'gender_group', 'registration_date', 'bib_number')
        # make sure output is ordered as the order in the fields
        ordered = True
    participant = fields.Nested(
        'ParticipantSchema', only=('first_name', 'last_name'))
    race = fields.Nested('RaceSchema', only=('name',))
    age_group = fields.Nested('AgeGroupSchema', only=('age_group',))


# single participant schema, which allows to retrieve single race
registration_schema = RegistrationSchema()
# multiple participants schema, which allows to retrieve multiple races
registrations_schema = RegistrationSchema(many=True)
