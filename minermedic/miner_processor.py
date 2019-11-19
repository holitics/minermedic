# miner_processor.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_processor import BaseProcessor
from phenome_core.core.base.logger import root_logger as logger
from phenome_core.core.handlers.action_handler import execute_single_action

"""

MinerProcessor subclass, based on BaseProcessor. 
Responsible for handling additional processing of all Miner objects during the poll cycle. 

"""


class MinerProcessor(BaseProcessor):

    def __init__(self):
        super(MinerProcessor, self).__init__()

    def init_object_states(self, object):

        # perform initial state checks on initial startup
        if not hasattr(object, 'last_poll_time'):
            # never been polled... reset the idle cycles count
            object.idle_cycles_count = 0

    def process_object(self, object, collector):

        # initialize object states, if needed
        self.init_object_states(object)

        # process the object (let the base processor handle main functionality)
        return super(MinerProcessor, self).process_object(object, collector)

    def process_object_states(self, object, results):

        """
        Simple state machine that handles default Miner Actions
        when specific Actions are not defined in the ActionModel.

        Returns:
            Boolean

        """

        if object is None:
            # should not happen
            logger.error("OBJECT is None")
            return False

        if object.admin_disabled:
            return False

        if not self.has_object_init_time_passed(object, results):
            # do not execute the state machine for items that are still initializing...
            return False

        logger.debug("process states for object {}".format(object.unique_id))

        states = self.get_object_state(object, results)

        # STEP 1 - REACHABILITY
        if states.poll_error == 1:

            if states.ping_error == 1:

                if hasattr(object, "power_state") and hasattr(object, "connected_outlet"):
                    # TODO - add error message to results/object?
                    return object.powercycle()
                else:
                    if object.wake_on_lan():
                        return True
                    else:
                        # there may be an object/subclass specific PowerCycle
                        return object.powercycle()

            else:
                # object does not poll, but can ping, try to restart
                return object.restart_miner()

        # STEP 2 - CHECK TEMPS
        if states.temp_error == 1:
            message = "TEMPS too high on {}".format(object.ip)
            return object.powercycle()

        # STEP 3 - CHIPS
        if states.chip_error == 1:
            message = "CHIP errors on {}".format(object.ip)
            return object.restart_miner()

        # STEP 4 - HASHRATE
        if states.hashrate_error == 1:
            message = "HASHRATE problems on {}".format(object.ip)
            # Actions should be handled now by the action_model

        # STEP 5 - UI
        if states.ui_error == 1:
            message = "UI down on {}".format(object.ip)
            return object.restart_miner()

        # STEP 6 - PROFITABILITY
        profitability = results.get_result(object.id, 'profitability')
        if profitability is None and object.is_powered_off():
            # this means we did not poll and we still need to run the profitability check
            return execute_single_action(object, results, 'check_profit', 'CRYPTO_MINER')

        return False
