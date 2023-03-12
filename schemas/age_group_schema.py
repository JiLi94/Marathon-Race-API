from main import ma

# create the participant scheme with Marshmallow
class AgeGroupSchema(ma.Schema):
    class Meta:
        # fields to output
        fields = ('id','min_age','max_age')
        # make sure output is ordered as the order in the fields
        ordered = True

# single participant schema, which allows to retrieve single race
age_group_schema = AgeGroupSchema()
# multiple participants schema, which allows to retrieve multiple races
age_groups_schema = AgeGroupSchema(many=True)
