# f2pool.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>


from minermedic.pools.base_pool import BasePool
from phenome_core.util.rest_api import RestAPI
from phenome_core.core.base.logger import root_logger as logger
from minermedic.pools.helper import get_algo_index, get_coin_cost, get_coin_index, \
    get_coin_cost_by_index, get_coin_name_by_symbol


# Returns bucketized 10-minute hashrate stats
# https://api.f2pool.com/{CURRENCY}/{USERNAME}/{WORKER}

"""

    F2Pool
    SEE:  https://www.f2pool.com/developer/api

"""


class F2Pool(BasePool):

    # for hashrate, profit, etc.
    _API_URL = "https://api.f2pool.com/{CURRENCY}/{USER_ID}"

    def __init__(self, pool, pool_attrs):

        super(F2Pool, self).__init__(pool, pool_attrs)

    def _build_api_hashrate_url(self, user_id, currency):

        # build the API URL
        url = self._API_URL.replace("{CURRENCY}", currency)
        url = url.replace("{USER_ID}", str(user_id))

        return url

    def get_last_complete_hashrate_from_history(self, json):

        hashrate = 0.0

        # get the latest hashrate (10 minute buckets)
        # Hashrate reported by Pool is H/S

        # values are keyed by timestamp but fill in every 10 minutes
        # because of that, we just will scan to the last filled bucket
        # usually i-2 if i is the index of the first bucket == 0

        # "2019-11-30T18:30:00Z": 171798692,
        # "2019-11-30T18:40:00Z": 264856317,
        # "2019-11-30T18:50:00Z": 3503503,
        # "2019-11-30T19:10:00Z": 0,
        # "2019-11-30T19:20:00Z": 0,

        buckets = json.get['hashrate_history']
        bucket_values = list(buckets.values())
        count = len(bucket_values)

        for idx in range(count):
            if bucket_values[count - idx] > 0:
                k = count - idx
                # set the index to the previous if possible
                if k - 1 >= 0:
                    k = k - 1
                hashrate = float(bucket_values[k])
                break

        return hashrate

    def get_pool_stats(self, results, miner, worker, algo, pool_id, pool_url):

        # initialize with a 0 hashrate
        hashrate = 0.0

        # get the coin from the pool URL
        # should be the format of: "ltc-us.f2pool.com:8888"

        pool_coin = pool_url.split(".")[0]
        if "-" in pool_coin:
            # seems pool location may be inside, remove that
            pool_coin = pool_coin.split("-")[0]

        # The F2Pool uses the CURRENCY in the API call but requires currency name
        # instead of the actual symbol - so we need to translate.
        # For example:
        # ltc == litecoin
        # btc == bitcoin
        # eth == ethereum

        # get the coin
        coin = get_coin_name_by_symbol(pool_coin)

        if coin is not None:

            # try to build a URL:
            url = self._build_api_hashrate_url(miner.coin_address, coin)

            # create an API object
            api = RestAPI(url=url, port=80)

            # get the data
            json = api.get_json()

            # hashrate from history - don't need this right now
            # hashrate = self.get_last_complete_hashrate_from_history(json)

            workers = json['workers']
            for worker_record in workers:
                if worker_record[0] == worker:
                    # current hashrate per worker
                    hashrate = float(worker_record[1])
                    break

        # get the algo
        algo_idx = get_algo_index(algo)
        if algo_idx == -1:
            return False

        # get the index and cost of the coin
        coin_idx = get_coin_index(pool_coin)
        coin_cost = get_coin_cost_by_index(coin_idx,'USD')
        coin_cost_btc = get_coin_cost('BTC', 'USD')
        coin_cost_ratio = coin_cost_btc/coin_cost

        # profit == BTC / GH / DAY
        # profit_btc_gh_day = pool['profit']

        # BUT we want to convert to GH/s to be consistent with profitability here
        # so force suffix to be GH
        speed_suffix = "GH"

        # must divide by 1G to get hashrate expressed in GH
        hashrate_ghs = (hashrate / 1000000000)

        # hack to get profit per day - need to verify with F2Pool support what this means and the units
        # would be better to get the value earned per worker rather than total value for all miners
        worker_count = int(json['worker_length'])
        profit_btc_gh_day = float(json['value_last_day'])/worker_count

        # We need the profitability to be in: COIN / speed_suffix / day
        # multiply by ratio of 'COIN' to BTC
        profit_coin_gh_day = profit_btc_gh_day * coin_cost_ratio

        # finally set the API results into the main results object
        results.populate_pool_results(miner, worker, pool_id, algo, algo_idx, coin_idx, coin_cost,
                                      profit_coin_gh_day, hashrate_ghs, None, speed_suffix)

        return True





