from main import ma


# create the participant scheme with Marshmallow
class RaceSchema(ma.Schema):
    class Meta:
        # fields to output
        fields = ('id','name','distance','date','start_time','cut_off_time','field_limit','start_line', 'finish_line', 'fee')
        # make sure output is ordered as the order in the fields
        ordered = True
        dump_only = ['id']

# single race schema, which allows to retrieve single race
race_schema = RaceSchema()
# multiple races schema, which allows to retrieve multiple races
races_schema = RaceSchema(many=True)
