from main import ma
from marshmallow import fields


class RegistrationSchema(ma.Schema):
    class Meta:
        # fields to output
        fields = ('participant', 'race', 'age_group','participant_id', 'race_id', 'age_group_id',
                  'gender_group', 'registration_date', 'bib_number')
        load_only = ['participant_id', 'race_id', 'age_group_id']
        # make sure output is ordered as the order in the fields
        ordered = True
    # only include first and last name of the participant
    participant = fields.Nested('ParticipantSchema', only = ['first_name', 'last_name'])
    # only show the name of race when dump
    race = fields.Pluck('RaceSchema', 'name')
    # only show the value of age_group when dump
    age_group = fields.Nested('AgeGroupSchema', only = ['min_age', 'max_age'])


# single registration schema, which allows to retrieve single registration
registration_schema = RegistrationSchema()
# multiple registration schema, which allows to retrieve multiple registrations
registrations_schema = RegistrationSchema(many=True)
