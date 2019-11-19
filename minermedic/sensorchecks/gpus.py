# gpus.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_action import BaseAction
from phenome_core.core.base.healthscore import compute_health_score

"""

    GPUCheck Healthcheck - checks miner GPUs for health issues

"""


class GPUCheck(BaseAction):

    def __init__(self):
        super(GPUCheck, self).__init__()

    def execute(self):

        object_states = self.results.object_states[self.object.id]
        gpu_stats = self.results.get_result(self.object.id, 'miner_chips')['status']
        gpus_missing = gpu_stats['-']
        gpus_total = gpu_stats['Os'] + gpu_stats['Xs'] + gpus_missing

        if gpus_missing > 0:
            self.error_message = "{} GPUs are not hashing".format(gpus_missing)
            self.has_error = True
            object_states.chip_error = 1

        # add the health score - make the "warning" level more than 10% of GPUs missing!
        compute_health_score(self.object, self.results, gpus_missing, int(gpus_total * .10), gpus_total)

        return True