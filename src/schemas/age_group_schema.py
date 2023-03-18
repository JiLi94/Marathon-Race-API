from main import ma


# create the participant scheme with Marshmallow
class AgeGroupSchema(ma.Schema):
    class Meta:
        # fields to output
        fields = ('id','min_age','max_age')
        # make sure output is ordered as the order in the fields
        ordered = True

# single age group schema, which allows to retrieve single age group
age_group_schema = AgeGroupSchema()
# multiple age group schema, which allows to retrieve multiple age groups
age_groups_schema = AgeGroupSchema(many=True)
