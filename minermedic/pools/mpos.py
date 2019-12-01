# mpos.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.util.rest_api import RestAPI
from phenome_core.core.base.logger import root_logger as logger

from minermedic.pools.base_pool import BasePool
from minermedic.pools.helper import get_algo_index, get_coin_cost, get_coin_index, get_coin_cost_by_index

"""

    MPOS Pool - should work with any mining Pool running MPOS software.
    TODO - break out MiningPoolHub specifics and add MPH subclass extending this.

"""

class MPOS(BasePool):

    # for coins, ports, profits
    _PROFITS_AND_STATS_URL = "https://miningpoolhub.com/index.php?page=api&action=getminingandprofitsstatistics"

    # for hashrate
    _API_URL = "https://{COIN}.miningpoolhub.com/index.php?" \
               "page=api&action=getuserhashrate&api_key={API_KEY}&id={USER_ID}"

    # These BOGUS values must be filled in with your OWN data or set into MINERMEDIC.INI File
    # Otherwise, they will have to be entered into the UI in the Object Configuration Screen
    _API_KEY = "ffff70711a5bbeed369699c1a0ca793cb2ab8ef49d9ca0d4896eac344f9eeffa"
    _USER_ID = "123456"

    _pools = None
    _pools_last_updated = 0
    _pool_info = None

    def __init__(self, pool, pool_attrs):

        super(MPOS, self).__init__(pool, pool_attrs)

        # now set pool info for the subsequent calls
        # get the port of the pool we are hitting and do a lookup
        algo_port = int(pool.split(":")[1])
        self._pool_info = MPOS._pools.get(algo_port)

    def build_creation_parameters(self, pool, pool_attrs, pool_classname):

        # get the default creation parameters
        params = super(MPOS, self).build_creation_parameters(pool, pool_attrs, pool_classname)

        # now, add some of our own, we need a property model for the MiningPoolHub,
        # as an API KEY and USER ID is required to hit the API

        if MPOS._pools is None:
            self.get_pool_info(pool)

        # get the port of the pool we are hitting
        algo_port = int(pool.split(":")[1])
        self._pool_info = MPOS._pools.get(algo_port)

        if 17000 <= algo_port <= 18000:
            # this is a direct ALGO pool
            params['unique_id'] = "Mining Pool Hub (" + self._pool_info[0]['algo'] + ")"
        else:
            # this is a COIN pool
            params['unique_id'] = "Mining Pool Hub (" + self._pool_info[0]['coin_name'] + ")"

        # define the property model - includes config params for the API Key and User ID needed to hit the API
        property_model = [
                {"name": "api_key", "description": "API KEY for Mining Pool", "property_type": "CONFIGURATION",
                 "value_type": "TEXT", "default": "", "attributes": [{"show_in_ui": "true", "required": 1}]},
                {"name": "user_id", "description": "USER ID for Mining Pool", "property_type": "CONFIGURATION",
                 "value_type": "INTEGER", "default": "0", "attributes": [{"show_in_ui": "true", "required": 1}]}]

        # set the property model into the creation params
        params['property_model'] = property_model

        # return
        return params

    def get_pool_info(self, pool):

        # get the port of the pool we are hitting
        # algo_port = int(pool.split(":")[1])

        # create an API object
        api = RestAPI(url=self._PROFITS_AND_STATS_URL, port=80)

        # get the data
        json = api.get_json()

        self._pool_info = []

        pools = {}

        if json:

            api_data = json['return']

            for record in api_data:

                port = int(record['port'])
                direct_port = int(record['direct_mining_algo_port'])
                algo = record['algo']
                profit = record['profit']
                coin_name = record['coin_name']

                pool_info = {"algo":algo, "coin_name":coin_name, "profit": profit}
                pool_info_direct = {"algo":algo, "coin_name":coin_name, "profit": profit}

                if pools.get(port) is None:
                    pools[port] = [pool_info]
                else:
                    pools[port].append(pool_info)

                if pools.get(direct_port) is None:
                    pools[direct_port] = [pool_info_direct]
                else:
                    pools[direct_port].append(pool_info_direct)

        # set this statically in the CLASS so all objects inherit this
        MPOS._pools = pools

    def _get_pool_url(self, index):
        pass

    def _get_api_key_and_user_id(self):

        from phenome import flask_app
        api_key = flask_app.config.get("MINING_POOL_HUB_API_KEY")
        user_id = flask_app.config.get("MINING_POOL_HUB_USER_ID")

        if api_key is None or len(api_key)==0:
            # try to get from object
            api_key = self._pool_object.api_key
            user_id = self._pool_object.user_id

        if api_key is not None and len(api_key) > 0:
            # we have an API key, does it match the current one in the pool object?
            try:
                if self._pool_object.api_key is None or (self._pool_object.api_key is not None and self._pool_object.api_key != api_key):
                    from phenome_core.core.database.db import db_session
                    self._pool_object.api_key = api_key
                    self._pool_object.user_id = user_id
                    db_session.commit()
            except:
                logger.error("Cannot commit API parameters for Mining Pool Hub Pool object")

        return api_key, user_id

    def _build_api_hashrate_url(self, api_key, user_id, coin):

        # build the API URL
        url = self._API_URL.replace("{COIN}",coin)
        url = url.replace("{API_KEY}", api_key)
        url = url.replace("{USER_ID}", str(user_id))

        return url

    def get_pool_stats(self, results, miner, worker, algo, pool_id, pool_url):

        # initialize with a 0 hashrate
        hashrate = 0.0

        # profit on MPOS site is measured in BTC/GH/DAY
        profit_btc_gh_day = 0.0

        if self._pool_info is None:
            # we are SOL
            logger.error("Cannot get needed POOL DATA from (getminingandprofitsstatistics) API call.")
            return False

        # get the API KEY and USER ID
        api_key, user_id = self._get_api_key_and_user_id()

        if api_key is None or len(api_key)==0 or user_id is None or user_id == 0:
            warn_msg = "MINING POOL HUB Needs API_KEY and USER_ID"
            warn_msg += " in order to retrieve Miner Data. Set using UI or .INI file"
            logger.warning(warn_msg)
            return False

        # Get the pool info, should be a list of potential multialgo pools based on port
        for pool in self._pool_info:
            algo = pool['algo']
            coin = pool['coin_name']

            # profit == BTC / GH / DAY
            profit_btc_gh_day = pool['profit']

            # try to build a URL:
            url = self._build_api_hashrate_url(api_key, user_id, coin)

            # create an API object
            api = RestAPI(url=url, port=80)

            # get the data
            json = api.get_json()
            if json:
                hashrate = json['getuserhashrate']['data']
                if hashrate > 0:
                    # this must be the right pool
                    break

        # get the algo
        algo_idx = get_algo_index(algo)
        if algo_idx == -1:
            return False

        # get the index and cost of the coin
        coin_idx = get_coin_index(coin)
        coin_cost = get_coin_cost_by_index(coin_idx,'USD')
        coin_cost_btc = get_coin_cost('BTC', 'USD')

        coin_cost_ratio = coin_cost_btc/coin_cost

        # The API is returning a number 1000 times larger than the WEB Dashboard, which is reporting in MH/S
        # We are going to surmise that the hashrate is reported in KH/s from the API

        # BUT we want to convert to GH/s to be consistent with profitability here
        # so force suffix to be GH
        speed_suffix = "GH"

        # and divide by 1M to get hashrate expressed in GH
        hashrate_ghs = (hashrate / 1000000)

        # We need the profitability to be in: COIN / speed_suffix / day
        # multiply by ratio of 'COIN' to BTC
        profit_coin_gh_day = profit_btc_gh_day * coin_cost_ratio

        # finally set the API results into the main results object
        results.populate_pool_results(miner, worker, pool_id, algo, algo_idx, coin_idx, coin_cost,
                                      profit_coin_gh_day, hashrate_ghs, None, speed_suffix)

        return True
