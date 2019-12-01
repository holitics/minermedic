# nicehash.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from minermedic.pools.base_pool import BasePool
from phenome_core.util.rest_api import RestAPI
from minermedic.pools.helper import get_algo_index, get_coin_index, get_coin_cost

"""

    NiceHash Pool - v2
    SEE:  https://www.nicehash.com/doc-api

"""

nicehash_algorithm_info = None


class NiceHashPool(BasePool):

    # OLD v1 API URL - does not work anymore
    # _MINER_URL = "https://api.nicehash.com/api?method=stats.provider.ex&addr={MINER}"

    # NEW v2 API URLs
    _MINER_URL = "https://api2.nicehash.com/main/api/v2/mining/external/{MINER}/rigs/"
    _ALGO_URL = "https://api2.nicehash.com/main/api/v2/mining/algorithms/"

    # with Nicehash, the coin is always BTC
    _DEFAULT_COIN_ = "BTC"

    def get_pool_stats(self, results, miner, worker, algo, pool_id, pool_url):

        # ensure we have an ALGO IDX (i.e. it is known by the system)
        algo_idx = get_algo_index(algo)

        if algo_idx is None:
            # TODO - throw an exception
            return False

        coin_idx = get_coin_index(self._DEFAULT_COIN_)

        # get the cost of the coin
        # TODO - get the currency from the config, do not assume USD
        # TODO - cache coin_cost for a period... (or implement REST API result cache)

        coin_cost = get_coin_cost(self._DEFAULT_COIN_,'USD')

        success = False

        # build the miner URL
        url = self._MINER_URL.replace("{MINER}",miner.coin_address)

        # create an API object
        api = RestAPI(url=url, port=80)

        # get the data
        json = api.get_json()

        if json:
            success = self.parse_json(json, results, miner, worker, pool_id, algo, algo_idx, coin_idx, coin_cost)

        return success

    def parse_json(self, json, results, miner, worker, pool, algo, algo_idx, coin_idx, coin_cost):

        success = False

        # get the records
        records = json['miningRigs']

        for record in records:

            if record.get('stats') is None:
                pass
                # TODO - should we log a warning no stats on NiceHash for this Coin / Address ?
            else:

                # get the NH algo key
                nice_algo_key = record['stats'][0]['algorithm']['enumName']

                # make sure we are looking at the correct algo
                nice_algo_idx = get_algo_index(nice_algo_key)

                # ensure the algo in this record matches the algo that we passed into the parse for this miner
                if nice_algo_idx == algo_idx:

                    try:

                        # get units suffix for this ALGO / Miner combo
                        speed_suffix = self.get_algo_units(nice_algo_key, results, miner, algo)

                        # get accepted hashrate to use in our profitability calcs

                        # NH is reporting as string (Big decimal scaled to 8 decimal points)
                        speed_accepted = float(record['stats'][0]['speedAccepted'])

                        # profitability is a measure of COIN / speed suffix / per DAY

                        # sometimes the profitability is in the actual stats record
                        stats = record['stats'][0]
                        profitability = stats.get('profitability')

                        if profitability is None:
                            # otherwise it is one level up in the algo record
                            profitability = record['profitability']

                        # NH is reporting profitability as (COIN / day) and the Results needs (COIN / hashrate / day)
                        # so also divide by the hashrate as our the populate method multiplies it back in later
                        profitability = float(profitability) / speed_accepted

                    except:

                        speed_accepted = 0.0
                        profitability = 0.0

                    # finally set the API results into the main results object
                    results.populate_pool_results(miner, worker, pool, algo, algo_idx, coin_idx, coin_cost,
                                                  profitability, speed_accepted, None, speed_suffix)

                    # break out of the loop
                    success = True
                    break

        return success

    def _build_nicehash_algoinfo_lookup(self):

        # NiceHash originally included this in their v1 API, but it is harder to get in their v2 API
        # we need to query another API call and cache it for later lookups

        global nicehash_algorithm_info

        # init the dictionary
        nicehash_algorithm_info = {}

        # create an API object
        api = RestAPI(url=self._ALGO_URL, port=80)

        # get the data
        json = api.get_json()

        if json:

            records = json['miningAlgorithms']
            # build the algo info dictionary
            for record in records:
                nicehash_algorithm_info[record['algorithm']] = record

    def get_algo_units(self, nice_algo_key, results, miner, algo):

        """
        Attempts to return the algo hashrate units for this miner and algo.

        Returns:
            String

        """

        algo_units = None

        # first let's see if we can get the units from NiceHash, it would be most accurate
        global nicehash_algorithm_info

        if nicehash_algorithm_info is None:
            self._build_nicehash_algoinfo_lookup()

        if nicehash_algorithm_info:
            try:
                algo_units = nicehash_algorithm_info.get(nice_algo_key)['displayMiningFactor']
            except KeyError:
                pass

        if algo_units is None:

            # if cannot get from NH, we need to get it from our internal configuration

            hash_info = results.get_hashrate_info(miner, algo)

            if hash_info is not None:
                # speed is in units of .. ? (e.g. GH/s)
                algo_units = hash_info['units']

        return algo_units


