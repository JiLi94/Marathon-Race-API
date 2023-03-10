from controllers.participants_controller import participants
from controllers.races_controller import races
from controllers.registrations_controller import registrations
from controllers.age_groups_controller import age_groups
from controllers.results_controller import results

registrable_controllers = [
    participants,
    races,
    registrations,
    age_groups,
    results
]