from main import ma
from marshmallow import fields


class RegistrationSchema(ma.Schema):
    class Meta:
        # fields to output
        fields = ('participant', 'race', 'age_group',
                  'gender_group', 'registration_date', 'bib_number')
        # make sure output is ordered as the order in the fields
        ordered = True
    # only include first and last name of the participant
    participant = fields.Nested('ParticipantSchema', only = ['first_name', 'last_name'])
    # only show the name of race when dump
    race = fields.Pluck('RaceSchema', 'name')
    # only show the value of age_group when dump
    age_group = fields.Pluck('AgeGroupSchema', 'age_group')


# single participant schema, which allows to retrieve single race
registration_schema = RegistrationSchema()
# multiple participants schema, which allows to retrieve multiple races
registrations_schema = RegistrationSchema(many=True)