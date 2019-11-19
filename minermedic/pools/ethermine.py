# ethermine.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from minermedic.pools.base_pool import BasePool
from phenome_core.util.rest_api import RestAPI
from minermedic.pools.helper import get_algo_index, get_coin_index, get_coin_cost

"""

EtherminePool

    This is the main Pool API for Ethermine.
    SEE:  https://ethermine.org/api/worker#monitoring
    
"""


class EtherminePool(BasePool):

    # PER WORKER
    _MINER_URL_PER_WORKER = "https://api.ethermine.org/miner/:{MINER}/worker/:{WORKER}/currentStats"

    # PER MINER
    _MINER_URL_PER_MINER = "https://api.ethermine.org/miner/:{MINER}/currentStats"

    # with Ethermine, the coin is Usually ETH, but could be ETC or ZCASH
    _DEFAULT_COIN_ = "ETH"

    def __init__(self, pool, pool_attrs):
        super(EtherminePool, self).__init__(pool, pool_attrs)

    def build_creation_parameters(self, pool, pool_attrs, pool_classname):

        # get the default creation parameters
        params = super(EtherminePool, self).build_creation_parameters(pool, pool_attrs, pool_classname)

        server_location = "US"

        if pool.startswith("eu1.etc") or pool.startswith("eu1.eth"):
            server_location = "Europe"
        elif pool.startswith("us1-etc"):
            server_location = "US"
        elif pool.startswith("us1.eth"):
            server_location = "US East"
        elif pool.startswith("us2.eth"):
            server_location = "US West"
        elif pool.startswith("asia1.eth"):
            server_location = "Asia"

        # Set the unique ID of the pool (give it a NAME, as the URL/IP may change)
        # POOL - LOCATION (COIN)
        params['unique_id'] = "ETHERMINE - " + server_location + " (" + self._DEFAULT_COIN_ + ")"

        return params

    def _clean_coin_address(self, miner):

        coin_address = miner.coin_address.lower()
        if coin_address.startswith('0x'):
            coin_address = coin_address[2:]
        elif coin_address.startswith('#0x'):
            coin_address = coin_address[3:]

        return coin_address

    def get_worker_stats(self, miner, worker):

        # build the miner URL
        url = self._MINER_URL_PER_WORKER.replace("{MINER}",self._clean_coin_address(miner)).replace("{WORKER}",worker)

        api = RestAPI(url=url, port=80)

        return api.get_json()

    def get_miner_stats(self, miner):

        # build the miner URL
        url = self._MINER_URL_PER_MINER.replace("{MINER}", self._clean_coin_address(miner))

        api = RestAPI(url=url, port=80)

        return api.get_json()

    def get_pool_stats(self, results, miner, worker, algo, pool_id):

        if algo == 'ethash':
            algo_idx = get_algo_index('daggerhashimoto')
        else:
            algo_idx = get_algo_index(algo)

        if algo_idx is -1:
            return False

        coin_idx = get_coin_index(self._DEFAULT_COIN_)

        # get the cost of the coin
        # TODO - get the currency from the config, do not assume USD
        coin_cost = get_coin_cost(self._DEFAULT_COIN_,'USD')

        success = False

        json = self.get_worker_stats(miner, worker)

        if json:
            success = self.parse_json(json, results, miner, worker, pool_id, algo, algo_idx, coin_idx, coin_cost)

        return success

    def parse_json(self, json, results, miner, worker, pool, algo, algo_idx, coin_idx, coin_cost):

        # get the record
        record = json['data']

        if record == 'NO DATA':

            # check coin switch?
            miner_coin_idx = None

            if hasattr(miner, 'coin_idx'):
                # we have been mining so far
                miner_coin_idx = miner.coin

            if miner_coin_idx is None or miner_coin_idx != coin_idx:
                # reset the coin address, maybe switched coin
                miner.coin_address = ''

            # no data, just fail
            return False

        # API call results, speed is in units of Hashes
        speed_suffix = 'H'

        try:
            # get accepted hashrate
            speed_accepted = float(record['currentHashrate'])
        except:
            speed_accepted = 0.0

        try:
            # get "reported" hashrate
            speed_reported = float(record['reportedHashrate'])
        except:
            speed_reported = None

        # now get the miner stats for profitability
        json_miner_stats = self.get_miner_stats(miner)

        # get the record
        record_miner_stats = json_miner_stats['data']

        try:
            coins_per_minute = float(record_miner_stats['coinsPerMin'])
        except:
            coins_per_minute = 0.0

        try:
            active_workers = float(record_miner_stats['activeWorkers'])
        except:
            active_workers = 1

        # profitability is a measure of COIN / speed suffix / per DAY
        # ETHERMINE only gives coin estimates per MINER per MINUTE, not per WORKER
        # so we need to average it out by dividing by the # of active workers
        profitability = ((coins_per_minute * (60 * 24))/speed_accepted)/active_workers

        # finally set the API results into the main results object
        results.populate_pool_results(miner, worker, pool, algo, algo_idx, coin_idx, coin_cost, profitability,
                                      speed_accepted, speed_reported, speed_suffix)

        # if we got here, we were successful
        return True

