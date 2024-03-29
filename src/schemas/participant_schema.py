from main import ma


# create the participant scheme with Marshmallow
class ParticipantSchema(ma.Schema):
    class Meta:
        # fields to output
        fields = ('id', 'first_name', 'last_name', 'email', 'mobile',
                  'password', 'date_of_birth', 'gender', 'admin')
        load_only = ['password', 'admin']
        dump_only = ['id', 'admin']
        # make sure output is ordered as the same the order in the fields
        ordered = True
    # registrations = fields.Nested('RegistrationSchema')


# single participant schema, which allows to retrieve single participant
participant_schema = ParticipantSchema()
# multiple participants schema, which allows to retrieve multiple participants
participants_schema = ParticipantSchema(many=True)
