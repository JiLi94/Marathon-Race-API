from main import ma
from marshmallow import fields


class ResultSchema(ma.Schema):
    class Meta:
        # fields to output
        fields = ('registration','id','registration_id','finished','start_at','finish_at','finish_time','pace')
        # make sure output is ordered as the order in the fields
        ordered = True

    # only extract the participant's name
    registration = fields.Pluck('RegistrationSchema', 'participant', data_key='participant')

# single result schema, which allows to retrieve single result
result_schema = ResultSchema()
# multiple result schema, which allows to retrieve multiple results
results_schema = ResultSchema(many=True)
