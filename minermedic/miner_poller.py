# miner_poller.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_poller import BasePoller

"""

MinerPoller subclass, based on BasePoller.

"""


class MinerPoller(BasePoller):

    def __init__(self, poller_results_class, poller_process_class):

        start_delay = 5
        super(MinerPoller, self).__init__(__name__, poller_results_class, poller_process_class, start_delay)

