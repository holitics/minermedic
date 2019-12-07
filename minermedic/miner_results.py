# miner_results.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

import ast, sys, copy
from datetime import timedelta

from phenome_core.core.database.model import api
from phenome_core.core.base.logger import root_logger as logger
from phenome_core.core.base.base_results import BaseResults, ObjectState
from phenome_core.util import math_functions
from minermedic.pools.helper import get_algo_index, get_algo_by_index, process_pool_apis
from minermedic.miners.helper import calculate_hashrates, get_power_usage_info_per_algo_per_minute


class MinerChipStats():

    """
    Helper object to describe chip states of Miners.
    """

    def __init__(self, chips_working, chips_defective, chips_missing, chips_total):
        self.chips_working = chips_working
        self.chips_defective = chips_defective
        self.chips_missing = chips_missing
        self.chips_total = chips_total


class MinerState(ObjectState):

    """
    The State object to use during processing of Miners.
    """

    def __init__(self):

        super(MinerState, self).__init__()

        # These are the key ERROR STATE KEYS
        # they can be toggled by the Generic Sensor Check if "error_state_key" is checked

        self.temp_error = 0
        self.chip_error = 0
        self.hashrate_error = 0
        self.ui_error = 0
        self.api_error = 0
        self.fan_error = 0
        self.profitable = 0


class MinerResults(BaseResults):

    """
    A specialized results object for polled and queried results during processing of Miners, but uses BaseResults
    as the base class to handle all general data handling. Handles specialized functions for miners like
    calculating profitability, hashrates, chips, fans, etc.
    """

    def __init__(self):

        super(MinerResults, self).__init__('CRYPTO_MINER')

        self.__init_hashrate_table()

    def __init_hashrate_table(self):

        self.hash_rate_overrides = {}
        self.hash_rate_per_model = {}

        model_values = api.get_default_propertyvalues_by_classtype_and_property('CRYPTO_MINER', 'hashrate')

        # set the expected values
        if model_values:
            for row in model_values:

                # create the list of dicts
                hashrate_by_algo = ast.literal_eval(row.value_text)

                for item in hashrate_by_algo:

                    algo = item['algo']
                    units = item['units']
                    hashrate = item['rate']
                    power = item['power']

                    row_key = row.model + "." + algo.replace("-", "")

                    self.hash_rate_per_model[row_key.lower()] = \
                        {"model": row.model, "algo": algo, "units": units,
                         "expected_rate": hashrate, "power": power,
                         "sum_current": 0, "sum_max": 0}

    def set_miner(self, miner):
        super(MinerResults, self).set_object(miner)

    def get_new_object_state(self):
        return MinerState()

    def set_miner_hashrate_override(self, miner, hashrate):
        self.hash_rate_overrides[miner.id] = hashrate

    def get_hashrate_info(self, miner, algo):

        """
        Retrieves HashRate Info by Miner and Algorithm
        :param miner: The Miner object
        :param algo: The Algo (String)
        :return: Dict of information for that Algo for that particular Miner
        """

        # Hack for some miners/pools
        if algo == "daggerhashimoto":
            algo = "ethash"

        # build the hashrate per model key
        key = miner.model.model + "." + algo.replace("-", "")

        # get the hashrate info for this model of miner
        hashrate_info = self.hash_rate_per_model.get(key.lower())

        if hashrate_info is not None:
            # are there any overrides set? If so, use those
            hashrate_override = self.hash_rate_overrides.get(miner.id)
            if hashrate_override is not None:
                hashrate_info['expected_rate'] = hashrate_override

        return hashrate_info

    def copy_result_data(self,results):

        # copy MinerResults specific info
        results.hash_rate_per_model = copy.copy(self.hash_rate_per_model)

        # now copy remaining results using superclass
        return super(MinerResults, self).copy_result_data(results)

    def populate_chip_results(self, miner, chips):

        """
        Build chip status and chip summary strings and populate the results
        :param miner: Miner Object
        :param chips: MinerChipStats Object
        :return: None
        """

        # build a status dict
        chip_status =  {'active': chips.chips_working,
                        'failed': chips.chips_defective,
                        'missing': chips.chips_missing}

        # get some working totals
        chips_bad = chips.chips_defective+chips.chips_missing
        chips_total = chips.chips_working + chips_bad
        chip_status_percent = (chips.chips_working / chips_total) * 100.0

        # set a result of chip status as a percent
        self.set_result(miner, 'miner_chips_status', chip_status_percent)

        # set the actual chip summary stats as a dict
        self.set_result(miner, 'miner_chips', {'detail': chip_status,
                                               'total': chips.chips_total,
                                               'active': chips.chips_working})

        # add a direct lookup summary string

        #if chips_bad == 0:
        #    chip_summary = str(chips.chips_working)
        #else:
        #    chip_summary = str(chips.chips_working) + "." + str(chips_bad)
        # self.set_result(miner, 'miner_chips_summary', {'summary': chip_summary})

    def populate_fan_results(self, miner, fan_speeds):

        """
        Populates the Fan Results for a Miner
        :param miner: Miner Object
        :param fan_speeds: (List) of Fan Speeds for that Miner
        :return: None
        """

        fan_avg = 0
        fan_status_pct = 100

        try:

            # get the avg fan
            fan_avg = math_functions.get_average_of_list(fan_speeds, 0)
            if fan_avg < 101:
                if fan_avg == 0:
                    fan_avg = ""
                else:
                    fan_avg = str(fan_avg) + "%"

            for fs in fan_speeds:
                if fs <= 0:
                    fan_status_pct = fan_status_pct - (1/len(fan_speeds))

            if fan_status_pct < 0:
                fan_status_pct = 0

        except Exception as ex:
            logger.error(ex)

        self.set_result(miner, 'fan_status', fan_status_pct)
        self.set_result(miner, 'fan_speeds', fan_speeds)
        self.set_result(miner, 'fan_speeds_avg', fan_avg)

    def __process_miner_pool_apis(self, miner, worker, algo, pool):

        # contact pools, do profitability stuff
        try:
            process_pool_apis(self, miner, worker, algo, pool)
        except Exception as ex:
            logger.error("Problem processing pool APIs for "
                         "pool '{}' algo '{}', error {}".format(pool, algo, ex))

    def __process_hashrate_calculations(self, miner, hashrate_ghs5s, algo):

        # it is possible with multi-algo miners and pools to switch the ALGO
        # let us double check the current algo vs the algo stored in the results
        # since the hashrate calcs depend on the ALGO

        try:
            algo_idx = get_algo_index(algo)
            algo_idx_from_pool = self.get_result(miner.id, 'algo')
            if algo_idx == -1 or (algo_idx_from_pool and algo_idx != algo_idx_from_pool):
                # get the changed algo
                algo = get_algo_by_index(algo_idx_from_pool)
        except:
            pass

        try:
            # do all hashrate stuff
            calculate_hashrates(self, miner, hashrate_ghs5s, algo)
        except:
            logger.error("Problem processing hashrate for "
                         "miner '{}' hashrate '{}'".format(miner.id, hashrate_ghs5s))

    def populate_miner_results(self, miner, elapsed_secs, worker, algo, pool, chips,
                               temps, fan_speeds, hashrate_ghs5s, hw_error_rate):

        """
        Populates all Miner Results for a particular poll cycle
        :param miner: Miner Object
        :param elapsed_secs: Number of Seconds that miner has been running
        :param worker: (String) worker ID
        :param algo: (String) Algorithm running on Miner at that time
        :param pool: The Pool ID being mined
        :param chips: MinerChipStats object
        :param temps: (list) of temps on miner
        :param fan_speeds: (list) of fan speeds on miner
        :param hashrate_ghs5s: "current" Hashrate in GigaHash/sec (over the last 5 or more seconds)
        :param hw_error_rate: rate of hardware errors
        :return:
        """

        self.set_result(miner, 'uptimes', timedelta(seconds=elapsed_secs))
        self.set_result(miner, 'temperatures', temps) # all temps
        self.set_result(miner, 'temperature', math_functions.get_average_of_list(temps, 0))
        self.set_result(miner, 'hw_error_rates', hw_error_rate)

        self.populate_chip_results(miner, chips)
        self.populate_fan_results(miner, fan_speeds)

        call_pool_apis = True
        call_hashrate_calcs = True

        try:
            if sys._unit_tests_running:
                call_pool_apis = sys._unit_tests_MINERMEDIC_CALL_POOL_APIS
                call_hashrate_calcs = sys._unit_tests_MINERMEDIC_CALL_HASHRATE_CALCS
        except:
            pass

        if call_pool_apis:
            try:
                self.__process_miner_pool_apis(miner, worker, algo, pool)
            except Exception as ex:
                logger.error("Problem while processing POOL APIS, pool='{}', error='{}'".format(pool, ex))

        if call_hashrate_calcs:
            try:
                self.__process_hashrate_calculations(miner, hashrate_ghs5s, algo)
            except Exception as ex:
                logger.error("Problem while processing Hashrate Calcs, "
                             "algo='{}', hashrate='{}', error='{}'".format(algo, hashrate_ghs5s, ex))

    def populate_pool_results(self, miner, worker, pool, algo, algo_idx, coin_idx, coin_cost,
                              profitability, speed_accepted, speed_reported, speed_suffix):

        """
        Populates all the pool results for a particular Miner.
        :param miner: Miner Object
        :param worker: (String) worker ID
        :param pool: (Integer) Pool ID
        :param algo: (String) Algo currently running on the miner
        :param algo_idx: (Integer) Algo index (internal)
        :param coin_idx: (Integer) Coin index (internal)
        :param coin_cost: (Float) Current cost of COIN being mined
        :param profitability: (Float) Current profitability in terms of COIN / SPEED / DAY
        :param speed_accepted: (Integer) Current Accepted Hashrate by the Pool (SPEED)
        :param speed_reported: (Integer) Current Hashrate reported by Miner
        :param speed_suffix: (String) The units of Hashrate (i.e. GH/s)
        :return: None
        """

        # Determine how much COIN is being generated per minute for the
        # accepted hashrate (stats are usually collected once each minute)
        # multiply the number of units of speed (speed accepted) by the profitability,
        # divided by 1440 minutes per day

        coin_generated_per_minute = (profitability * speed_accepted) / (60 * 24)

        # compute amount of power used and the cost of that power, per minute
        power_used, power_used_cost = get_power_usage_info_per_algo_per_minute(self, miner, algo)

        # must always set worker, algo, pool
        self.set_result(miner, 'worker', worker)
        self.set_result(miner, 'algo', algo_idx)
        self.set_result(miner, 'pool', pool)

        # set the algo stats - for hashrate calculations later

        self.set_result(miner, 'hashrates_by_algo',
                        {algo: {'accepted': speed_accepted,
                                'reported': speed_reported,
                                'speed_suffix': speed_suffix}})

        # derived stats
        self.set_result(miner, 'power_used', power_used)
        self.set_result(miner, 'power_used_cost', power_used_cost)
        self.set_result(miner, 'coin', coin_idx)
        self.set_result(miner, 'coin_cost', coin_cost)
        self.set_result(miner, 'coin_mined', coin_generated_per_minute)

        # save the current coin index in the miner
        miner.coin_idx = coin_idx

        # how much would it cost to purchase this much generated coin, instead?
        coin_purchase_cost = (coin_cost * coin_generated_per_minute)
        self.set_result(miner, 'coin_purchase_cost', coin_purchase_cost)

        # did we get power used cost so we can determine Profitability?
        if power_used_cost is not None and power_used_cost != 0:

            # PROFITABILITY - (cost to buy) / (cost to mine) >1 is profitable
            self.set_result(miner, 'profitability', (coin_purchase_cost / power_used_cost))

            # BOOLEAN is it profitable
            self.set_result(miner, 'profitable', (coin_purchase_cost > power_used_cost))
