# base_miner.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome.extensions.classtypes.OBJECT.powered_object import PoweredObject
from phenome_core.core.base.base_action import BaseAction
from phenome_core.util import time_functions
from phenome_core.core.helpers import config_helpers
from phenome_core.core.base.logger import root_logger as logger
from abc import abstractmethod


"""

BaseMiner 

This is the base definition of all CRYPTO_MINER objects and inherits from PoweredObject and BaseAction.

All Miners should subclass this object in order to provide a 
vendor specific implementation of data retrieval and actions.

"""


class BaseMiner(PoweredObject, BaseAction):

    # set the classtype of all objects subclassing BaseMiner to be a CRYPTO_MINER type
    CLASSTYPE = "CRYPTO_MINER"

    def __init__(self):
        super(BaseMiner, self).__init__()

    @abstractmethod
    def poll(self, results):

        """
        Poll method communicates to the Miner and stores statistics in the MinerResults object.
        ABSTRACT. Actual miner specific code must be implemented in each Miner Subclass.
        """

        pass

    def restart_miner(self):

        """
        Attempts to restart the miner. This is a wrapper for "miner.restart()".
        The actual "restart" method must be implemented individually for each subclass of Miner.

        Returns:
            boolean

        """

        success = False

        # can we still ping this miner?
        if self.object_states.ping_error == 0:

            # we can still ping it, so attempt to restart miner
            logger.debug("Attempt to restart object {}".format(self.id))

            success = False
            self.__init_restart_delay(self.object)

            # should we restart it?
            restart = time_functions.get_timeout_expired(self.last_restart_time, self.restart_delay)

            if restart:

                # do the actual restart
                success = self.restart()

                # set the last restart attempt time
                self.last_restart_time = time_functions.current_milli_time()

                if success:

                    # reset the init state so state machine does not try to auto-powercycle, etc.
                    self._reset_init_state()

                    logger.info("Restarted Miner {}(ID={})".format(self.object.unique_id, self.object.id))
                else:
                    # according to state machine diagram, if restart fails, powercycle (OR OFF)
                    success = self.powercycle()

        return success

    def restart(self):
        # PLACEHOLDER. Implement in subclass if a miner supports a restart command, otherwise return FALSE
        return False

    def __init_restart_delay(self, object):

        if object.restart_delay == 0:
            # restart delay is in MS
            object.restart_delay = config_helpers.get_config_value("MISC", "device_restart_delay_ms", 300000)
