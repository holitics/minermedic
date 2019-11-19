# chips.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_action import BaseAction
from phenome_core.core.base.healthscore import compute_health_score
from phenome_core.core.helpers.numeric_helpers import percent_to_float

"""

    ChipCheck Healthcheck - checks miner chips for health issues

"""


class ChipCheck(BaseAction):

    def __init__(self):
        super(ChipCheck, self).__init__()

    def execute(self):

        chips_stats = self.results.get_result(self.object.id, 'miner_chips')['status']
        object_states = self.results.object_states[self.object.id]

        chips_working = chips_stats['Os']
        chips_defective = chips_stats['Xs']
        chips_missing = chips_stats['-']

        chips_not_working = chips_defective + chips_missing
        chips_total = chips_working + chips_not_working

        if chips_not_working == chips_total and chips_defective == 0:
            # the miner is just not hashing right now
            # this will be caught correctly with IDLE check
            return True

        error_pct = percent_to_float(self.args.get('error_level'))
        warn_pct = percent_to_float(self.args.get('warning_level'))

        # a chip error is going to be defined as more than X% of 'chips' not working
        self.has_error = (1-(chips_not_working/chips_total)) < error_pct
        self.has_warning = (1-(chips_not_working/chips_total)) < warn_pct

        if chips_defective > 0:
            self.error_message = "{} chips are defective".format(chips_defective)

        if chips_missing + chips_defective > chips_working:
            self.error_message = "{}/{} chips are missing".format((chips_not_working), chips_total)

        object_states.chip_error = int(self.has_error)

        # add the health score
        # start adding to the score if there are more than X% of the chips acting up!
        compute_health_score(self.object, self.results, (chips_defective + chips_missing), int(chips_total * error_pct), chips_total)

        # TODO - do something with WARNING??

        return True