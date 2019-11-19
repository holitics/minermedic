# hashrate.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_action import BaseAction
from phenome_core.core.base.healthscore import compute_health_score
from phenome_core.core.helpers.numeric_helpers import percent_to_float
from phenome_core.core.base.logger import root_logger as logger

from minermedic.miners.helper import get_converted_hashrate

"""

    HashCheck Healthcheck - checks miner hashrates

"""


class HashCheck(BaseAction):

    _ERROR_STATE_KEY_ = "hashrate_error"

    def __init__(self):
        super(HashCheck, self).__init__()

    def execute(self):

        # ok get the hashrate info from the miner
        hashrate_info_miner = self.results.get_result(self.object.id, 'hashrates')

        if hashrate_info_miner is None:
            # first time through here, exit
            return True

        # get some basic info from the miner hashrate stats
        current_hashrate = hashrate_info_miner.get('current')
        hashrate_units = hashrate_info_miner.get('units')

        if current_hashrate == 0:
            # the miner is just not hashing right now
            # should we add to the health score or just pass?
            # this will probably get taken care of by IDLE check
            return True

        # init some vars for the pool hashrate stats
        reported_hashrate_pool = None
        accepted_hashrate_pool = None
        current_hashrate_pool = 0
        speed_suffix_pool = None

        #  ok get the hashrate info from the pool
        hashrate_info_pool = self.results.get_result(self.object.id, 'hashrates_by_algo')

        pool_name = None

        if hashrate_info_pool is not None and len(hashrate_info_pool)==1:

            # TODO - if it is larger than 1, check the current algo
            # that the miner is processing and match the hashrate by algo

            for key, value in hashrate_info_pool.items():

                pool_name = key

                # the accepted hashrate from the pool (this is really what you are getting paid for)
                accepted_hashrate_pool = value.get('accepted')

                # some pools include "reported" hashrate, should represent how much your miner is hashing,
                # and it should be very close if not the same as the "current_hashrate" reported directly
                # from your miner.
                reported_hashrate_pool = value.get('reported')

                # get the speed of the hashing rate from the pool for conversions
                speed_suffix_pool = value.get('speed_suffix')

                break

        # first check if there could be a problem from the pool's perspective
        if accepted_hashrate_pool is not None and speed_suffix_pool is not None:
            current_hashrate_pool = get_converted_hashrate(accepted_hashrate_pool, speed_suffix_pool, hashrate_units)
            reported_hashrate_pool = get_converted_hashrate(reported_hashrate_pool, speed_suffix_pool, hashrate_units)

        # TODO - possibly use moving average in the future
        # https://stackoverflow.com/questions/13728392/moving-average-or-running-mean

        # for now, use the max hashrate achieved thus far to check expected hashrate for the miner

        max_hashrate = hashrate_info_miner['max']
        units = hashrate_info_miner['units']
        error_level = self.args['error_level']
        warning_level = self.args['warning_level']

        has_error_miner = False
        has_error_pool = False
        has_warn_pool = False
        has_warn_miner = False

        # Handle Error Levels

        if error_level is None:
            error_pct = 0
        else:
            error_pct = percent_to_float(error_level)
            has_error_pool = (current_hashrate_pool < (error_pct * max_hashrate))
            has_error_miner = (current_hashrate < (error_pct * max_hashrate))
            # do not take into account the pool hashrate to trigger an "ERROR"...
            self.has_error = (has_error_miner)

        # Handle Warning Levels

        if warning_level is None:
            warn_pct = 0
        else:
            warn_pct = percent_to_float(warning_level)
            has_warn_pool = (current_hashrate_pool < (warn_pct * max_hashrate))
            has_warn_miner = (current_hashrate < (warn_pct * max_hashrate))
            self.has_warning = (has_warn_miner or has_warn_pool)

        if self.has_error:
            self.error_message = self._build_error_message(
                "Miner '{}'".format(self.object.unique_id),current_hashrate, units, "error", error_level, max_hashrate)

        elif self.has_warning:
            if has_warn_pool:
                self.error_message = self._build_error_message(
                    "Pool '{}'".format(pool_name), current_hashrate_pool, units, "warning", error_level, max_hashrate)
            else:
                self.error_message = self._build_error_message(
                    "Miner '{}'".format(self.object.unique_id), current_hashrate, units, "warning", error_level, max_hashrate)

        # do not process health scores if both levels are not set
        if error_pct == 0 or warn_pct == 0:
            return False

        if self.has_error or self.has_warning:

            # now, determine amount of hashrate "missing" from the total potential hashrate
            if has_error_pool or has_warn_pool:
                missing_hashrate = round(max_hashrate - current_hashrate_pool)
            else:
                missing_hashrate = round(max_hashrate - current_hashrate)

            warning_missing_hashrate = round(max_hashrate - (max_hashrate * warn_pct))
            error_missing_hashrate = round(max_hashrate - (max_hashrate * error_pct))
            compute_health_score(self.object, self.results, missing_hashrate, warning_missing_hashrate, error_missing_hashrate)

            try:
                if self.has_error:
                    if self.results.object_states.get(self.object.id) is not None:
                        # set the object state flag in the case object states are used
                        self.results.object_states[self.object.id].__setattr__(self._ERROR_STATE_KEY_,1)
            except:
                logger.error(
                    "Problem setting error_state_key '{}' "
                    "for OBJECT ID={}".format(self._ERROR_STATE_KEY_, self.object.id))

        else:

            # some special cases?

            # FOR DEBUG
            if current_hashrate > 0 and current_hashrate_pool > 0 and \
                    reported_hashrate_pool is not None and reported_hashrate_pool == 0:

                # there is a problem. the reported rate should be around one of these rates.
                logger.debug("Reported Hashrate from the pool is 0 for miner '{}'. "
                             "Something could be wrong with miner or the miner "
                             "is not reporting hashrate to the pool".format(self.object.unique_id))

        return True

    def _build_error_message(self, what, current_hashrate, units, level_type, level, max_hashrate):

        return "{} hashrate {} {} is below {} threshold of {} based on max-rate of" \
               " {} {}".format(what, int(current_hashrate), units, level_type, level, max_hashrate, units)

