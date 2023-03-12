from main import ma
from marshmallow import fields


class ResultSchema(ma.Schema):
    class Meta:
        # fields to output
        fields = ('registration','finished','start_at','finish_at','finish_time','pace')
        # load_only = ['participant_id', 'race_id', 'age_group_id']
        # make sure output is ordered as the order in the fields
        ordered = True
    registration = fields.Nested('RegistrationSchema')


# single result schema, which allows to retrieve single result
result_schema = ResultSchema()
# multiple result schema, which allows to retrieve multiple results
results_schema = ResultSchema(many=True)
