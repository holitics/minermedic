# base_miner.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome.extensions.classtypes.OBJECT.powered_object import PoweredObject
from phenome_core.core.base.base_action import BaseAction
from phenome_core.util import time_functions
from phenome_core.core.helpers import config_helpers
from phenome_core.core.base.logger import root_logger as logger
from abc import abstractmethod
from minermedic.miners.helper import parse_worker_string
from minermedic.api import cgminer
from minermedic.pools.helper import get_algo
from phenome_core.util.time_functions import get_total_minutes_seconds_from_clock_time, \
    get_total_minutes_seconds_from_timestamp


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

    def poll_pool_stats(miner):

        """
        Pool Stats are retrieved from the Miner. Generic, shared call.
        """

        last_share_time = 0
        miner.algo = None

        # WORKER, POOL, ALGO, LAST SHARE TIME
        miner_pools = cgminer.get_pools(miner.ip)

        for miner_pool in miner_pools['POOLS']:
            miner_pool_status = miner_pool.get('Status')
            miner_pool_stratum_active = miner_pool.get('Stratum_Active')

            if (miner_pool_status is not None and miner_pool_status == "Alive") or (
                    miner_pool_stratum_active is not None and miner_pool_stratum_active == True):
                # pull pertinent information
                worker = miner_pool['User']
                # get the PORT as well, different pools/algos at different ports
                miner.pool = miner_pool['URL'].split("//", 1)[-1]
                miner.algo = get_algo(miner.pool)
                last_share_time = miner_pool.get('Last Share Time')
                break

        if miner.algo is None:
            miner.algo = miner.hashrate[0]['algo']

        # IDLE STATE
        if last_share_time is not None:

            # convert last share time to minutes (i.e. share cycles) and then compare and set if needed
            if isinstance(last_share_time, int):
                last_share_minutes, last_share_seconds = get_total_minutes_seconds_from_timestamp(last_share_time)
            else:
                last_share_minutes, last_share_seconds = get_total_minutes_seconds_from_clock_time(last_share_time)

            if last_share_minutes >= 1:

                if miner.last_share_time is not None and miner.last_share_time > 0:
                    last_share_delta = last_share_minutes - miner.last_share_time
                else:
                    last_share_delta = 0

                # set the last share time
                miner.last_share_time = last_share_minutes

                if last_share_delta >=2:
                    logger.debug("process_miner() - miner=" + str(miner.id) + " - Miner is IDLE.")
                    miner.idle_cycles_count = last_share_delta
                elif miner.idle_cycles_count > 1:
                    # reset it
                    miner.idle_cycles_count = 0

        # get the coin address and worker
        miner.coin_address, miner.worker = parse_worker_string(miner, worker)

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
