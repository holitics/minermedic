# ui.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_action import BaseAction

"""

    UICheck Healthcheck - checks miner WEB port to see if web service is responding

"""

class UICheck(BaseAction):

    def __init__(self):
        super(UICheck, self).__init__()

    def execute(self):

        # TODO
        return True

