# miner_actions.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_action import BaseAction


class MinerActions(BaseAction):

    def __init__(self):
        super(MinerActions, self).__init__()

    def execute(self):
        # placeholder - TBI in subclasses
        pass

    def restart(self):
        # attempt to restart miner
        return False

    def reboot(self):
        return False

    def powercycle(self):
        return False

    def poweron(self):
        pass

    def poweroff(self):
        pass


