# profitability.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_action import BaseAction
from phenome_core.util.time_functions import current_milli_time
from phenome_core.core.base.healthscore import add_health_score
from phenome_core.core.helpers.result_helpers import get_datamodel_data_by_object_id
from phenome_core.core.base.logger import root_logger as logger
from phenome_core.core.handlers import message_handler
from phenome_core.core.helpers.string_helpers import str_to_bool

import math, logging

"""

    ProfitCheck Healthcheck - checks miner profit and will shut down or start up miners based on profitability.

"""


class ProfitCheck(BaseAction):

    HEALTH_SCORE_ADJUSTMENT = 5

    def __init__(self):
        super(ProfitCheck, self).__init__()

    def execute(self):

        if self.object.admin_disabled:
            # no running Profitability checks on ADMIN Disabled devices
            return False

        # is it currently profitable (i.e. this last poll period)?
        profitability_results = self.results.get_result(self.object.id, 'profitability')

        # when was the last time we checked the profitability
        last_profitcheck_time = self.object.last_profitcheck_time

        # when is the NEXT time we are supposed to check profitability (set only on profitability FAILURE)
        next_recheck_time = self.object.next_profitcheck_time

        if last_profitcheck_time == 0:
            self.object.last_profitcheck_time = current_milli_time()
            return False

        number_samples = int(self.args.get('sample_count'))
        if number_samples>30:
            # since we are working with RAW data here, and there are only 60 minutes of samples
            # we want to use half that so we have two datasets to compare profitability
            number_samples = 30

        if current_milli_time() < (last_profitcheck_time + (number_samples * 60000)):
            return False

        powered_on = self.object.is_powered_on()
        has_power_source = self.object.has_power_source()

        if next_recheck_time > 0 and self.object.profitable == 0:
            if powered_on == False and has_power_source and next_recheck_time < current_milli_time():
                # the appropriate TIME has passed since the Miner was powered DOWN
                # now it is time to power it back up and run the profitability checks for X samples
                self.object.next_profitcheck_time = 0
                return self.object.power_on("Starting Profitability Check")
            elif next_recheck_time > current_milli_time():
                # somehow we are powered ON but we are still not profitable and we are NOT supposed to check yet
                # so just adjust health score and get out of the check
                add_health_score(self.object, self.results, self.HEALTH_SCORE_ADJUSTMENT)
                return False

        # get the entire profitability dataset, if available (up to entire HOUR)
        period_start = current_milli_time() - (60 * 60000)

        # get the dataframe for 'profitability' for this object, return all RAW data (defaults to "HOUR")
        df = get_datamodel_data_by_object_id('CRYPTO_MINER', period_start, None,
                                             ['profitability'], [self.object.id], False)

        if df is None:
            logger.debug("No profit data collected yet for Miner {}".format(self.object.unique_id))
            return False
        else:
            # remove any NaNs just in case
            df.dropna(inplace=True)

        # set a baseline profitability target
        profit_target = 1.0  # 1 is "breakeven"
        pt = self.args.get('profit_target')
        if pt is not None:
            profit_target = float(pt)

        profit_mean = df.mean()[0]
        if math.isnan(profit_mean) or profitability_results is None:
            # there is no data in there.
            return False

        # get some basic stats for the debug log
        p_pct_current = (float(profitability_results) / profit_target * 100)
        p_pct_sample = (profit_mean / profit_target * 100)

        logger.debug("Miner {} profitability: '{}%' (current) and '{}%' (period) of '{}' (target)".format(
            self.object.unique_id, p_pct_current, p_pct_sample, profit_target))

        notify_on_change = str_to_bool(self.args.get('notify_on_change'))
        message = None

        # now see if we have enough samples
        total_samples = len(df)
        logger.debug("{} samples in profit dataframe, need {}".format(total_samples, (number_samples*2)))

        if total_samples>=((number_samples*2)-1):

            # OK, now we are really checking, so set the last profitcheck time
            self.object.last_profitcheck_time = current_milli_time()

            df_samples = df.tail(number_samples)
            df_history = df.head(total_samples-number_samples)
            current_avg = df_samples.mean()[0]
            hist_avg = df_history.mean()[0]
            profitable_currently = (current_avg > profit_target)
            profitable_historically = (hist_avg > profit_target)

            powerdown_when_not_profitable = self.args.get('powerdown_when_not_profitable')
            powerup_when_profitable = self.args.get('powerup_when_profitable')

            if profitable_currently and (profitable_historically is False or self.object.profitable == 0):

                # this is great, the unit is now profitable again - it was previously UNPROFITABLE
                message = "Miner is currently profitable!"

                if powered_on == False and has_power_source and powerup_when_profitable:
                    self.object.power_on(message)
                    message = None

                # reset profitability and recheck
                self.object.profitable = 1
                self.object.next_profitcheck_time = 0

            elif profitable_currently is False:

                if profitable_historically is True or self.object.profitable == 1:
                    message = "Miner has become unprofitable"
                else:
                    message = "Miner is not profitable"

                if powered_on and has_power_source and powerdown_when_not_profitable:
                    self.object.power_off(message)
                    message = None

                # set the next recheck time
                self.object.next_profitcheck_time = current_milli_time() + int(self.args.get('recheck_delay'))

                # FLAG as unprofitable
                self.object.profitable = 0

                # add to the health score
                add_health_score(self.object, self.results, self.HEALTH_SCORE_ADJUSTMENT)

        # Finally, handle notification, if needed
        if message is not None:
            message_handler.log(None, message, self.object, logging.INFO, notify_on_change)