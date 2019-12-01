# helper.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.globals import global_enums
from phenome_core.util.rest_api import RestAPI
from phenome_core.core.base.logger import root_logger as logger

from pydoc import locate
import re, sys

# dictionary of pools
pool_lookups = {}

# dictionary of pool objects
pool_objects = {}

# dictionary of COIN symbols by RAW coin name lookups
coin_symbol_by_name = {}

# quick lookup of coin ID by NAME
coin_index_by_name = {}

# quick lookup to get coin SYMBOL by ID
coin_symbol_by_index = {}

# quick lookup to get coin NAME by SYMBOL
coin_name_by_symbol = {}

# some URLs
coin_cost_url = "https://min-api.cryptocompare.com/data/price?fsym={COIN}&tsyms={CURRENCY}"

"""

Pool Helper functions 

Contains a number of functions to help with parsing pool results, coin lookups, algos, etc.

"""


def get_coin_name_by_symbol(coin_symbol):

    """
    Retrieves a coin NAME when passed a coin SYMBOL

    Returns:
        String

    """

    coin_name = coin_name_by_symbol.get(coin_symbol.lower())

    if coin_name is None:
        # init the coin_symbol_by_name with names and symbols
        coin_index = get_coin_index_by_name(coin_symbol)
        # now retrieve it
        coin_name = coin_name_by_symbol[coin_symbol.lower()]

    return coin_name


def get_coin_symbol_by_index(coin_index):

    """
    Retrieves a coin SYMBOL when passed a coin INDEX

    Returns:
        String

    """

    coin_symbol = coin_symbol_by_index.get(coin_index)
    if coin_symbol is not None:
        return coin_symbol

    # need to do a real lookup
    coins_reverse = global_enums.get_reverse_map_enum('_COINS_')

    try:
        coin_symbol = coins_reverse[coin_index]
    except KeyError:
        coin_symbol = None

    if coin_symbol is not None:
        coin_symbol_by_index[coin_index] = coin_symbol

    return coin_symbol


def get_coin_cost_by_index(coin_index, currency):

    """
    Retrieves cost of a coin when passed a coin INDEX and currency

    Returns:
        Float

    """

    coin_symbol = get_coin_symbol_by_index(coin_index)

    if coin_symbol is not None:
        return get_coin_cost(coin_symbol, currency)

    return None


def get_coin_cost(coin, currency):

    """
    Retrieves cost of a coin when passed a coin SYMBOL and currency

    Returns:
        Float

    """

    url = coin_cost_url.replace("{COIN}",coin).replace("{CURRENCY}",currency)
    price = 0.0

    api = RestAPI(url=url, port=80)
    json = api.get_json()

    if json:
        price = json[currency]

    return price


def _clean_string_for_key(text):

    new_text = text.replace("-", "").replace(" ", "")
    return new_text.lower()


def get_coin_index_by_name(coin):

    """
    Retrieves coin INDEX when passed a coin NAME

    Returns:
        Integer

    """

    coin_index = coin_index_by_name.get(coin)

    if coin_index is not None:
        return coin_index
    else:
        coin_index = -1

    # now the hard work begins
    coin_details = global_enums.get_enum_details('_COINS_')

    if len(coin_symbol_by_name) == 0 or len(coin_symbol_by_name)!=len(coin_details):
        # need to build coin lookups
        for c_detail in coin_details:

            # build the keys
            coin_name_key = _clean_string_for_key(c_detail.value['CoinName'])
            coin_name_key_symbol = _clean_string_for_key(c_detail.value['Symbol']).lower()

            coin_symbol_by_name[coin_name_key] = c_detail.name
            coin_name_by_symbol[coin_name_key_symbol] = coin_name_key

    # now do a lookup in the coin name
    coin_name_clean = _clean_string_for_key(coin)
    coin_symbol = coin_symbol_by_name.get(coin_name_clean)

    if coin_symbol is None and coin_name_by_symbol.get(coin.lower()) is not None:
        coin_symbol = coin.upper()

    if coin_symbol is None:
        # one more try
        coin_name_clean = _clean_string_for_key(coin.split("-")[0])
        coin_symbol = coin_symbol_by_name.get(coin_name_clean)

    if coin_symbol is not None:
        try:
            coin_index = int(coin_details[coin_symbol].value['Id'])
        except KeyError:
            coin_index = -1

    if coin_index >= 0:
        # we found it, add to the lookup for next time
        coin_index_by_name[coin] = coin_index

    return coin_index


def get_coin_index(coin):

    """
    Retrieves coin INDEX when passed a coin SYMBOL

    Returns:
        Integer

    """

    # this method assumes SYMBOL is passed in
    coins = global_enums.get_enum('_COINS_')

    try:
        # coin symbol keys are stored in UPPERCASE
        coin_index = coins[coin.upper()].value
    except KeyError:
        coin_index = -1
    except Exception as ex:
        logger.exception(ex)

    if coin_index == -1:
        coin_index = get_coin_index_by_name(coin)

        if coin_index == -1 and len(coins) <= 100:

            # By default when we load up initially, we just retrieve the top 100 coins
            # now we need to get ALL the coins since this coin is obviously not loaded
            # we will have to wait about 5 seconds to pull the data and parse

            global_enums.reload_api_enum("_COINS_", True)

            # now try again, with ALL the coins
            coin_index = get_coin_index_by_name(coin)

    return coin_index


def get_algo_by_index(algo_index):

    """
    Retrieves algo when passed an algo INDEX

    Returns:
        Integer

    """

    algo = None

    # get the algos enum
    enum_algos = global_enums.get_reverse_map_enum('_ALGOS_')
    try:
        algo = enum_algos[algo_index]
    except KeyError:
        logger.warning("There is no Algo Index '{}' defined".format(algo_index))

    return algo


def get_algo_index(algo):

    """
    Retrieves algo INDEX when passed an algo

    Returns:
        Integer

    """

    # get the algos enum
    enum_algos = global_enums.get_enum('_ALGOS_')

    # clean the algo string
    algo_str_clean = algo.replace("-","").lower()

    try:
        algo_idx = enum_algos[algo_str_clean].value
    except KeyError:
        logger.warning("There is no Algo '{}' defined. "
                       "Check the _ALGOS_ ENUM for the key {}.".format(algo, algo_str_clean))
        algo_idx = -1

    return algo_idx


def get_algo(mining_pool):

    """
    Retrieves algo when passed mining pool URL.
    Very often the algo and coin are actually in the POOL URL.

    Returns:
        String

    """

    # returns the algorithm string
    algo = None

    if mining_pool is not None:
        x = mining_pool.count('.')
        if x >= 3:
            algo = mining_pool.split(".")[0]

    return algo


def process_pool_apis(results, miner, worker, algo, pool):

    """
    Processes all pool APIs for the specific pool

    Returns:
        None

    """

    success = False
    pool_attrs = None
    pool_class = None
    pool_not_supported = False

    if pool not in pool_lookups:

        # get the pool classnames enum
        enum_pools = global_enums.get_enum_details('_POOL_STATS_CLASSNAMES_')

        for enum_pool in enum_pools:

            pool_attrs = enum_pool.value[0]
            pool_url_match = pool_attrs['url_match']
            m = re.search(pool_url_match, pool)

            if m is not None:

                # add the name to the attributes
                pool_attrs['name'] = enum_pool.name

                # add the attributes to the list.
                pool_lookups[pool] = pool_attrs

                break

            else:

                pool_attrs = None

    else:
        pool_attrs = pool_lookups[pool]

    if pool_attrs is not None:

        pool_id = pool_attrs["value"]
        pool_classname = pool_attrs["classname"]

        # get the model class to operate with
        pool_class = locate(pool_classname)

        unit_tests_running = False

        if pool_class is None:
            logger.error("pool classname {} could not be initialized".format(pool_classname))
        else:

            # create the mining pool
            mining_pool = pool_class(pool, pool_attrs)

            try:
                unit_tests_running = sys._unit_tests_running
            except:
                pass

            if not unit_tests_running:

                try:
                    # add the relations (we do not need them for unit tests)
                    mining_pool.relate(miner)
                except Exception as ex:
                    logger.debug(ex)

            # execute the "get_pool_stats(...)" method
            success = mining_pool.get_pool_stats(results, miner, worker, algo, int(pool_id), pool)

    else:
        pool_not_supported = True
        logger.warning("POOL {} not yet supported".format(pool))
        # TODO - issue notification? log an issue on GitHub?

    if success is False and pool_not_supported is False:
        # There is a legitimate error...
        if pool_class is None:
            logger.error("No Pool support found for Pool/Model/Algo {}/{}/{}".format(pool, miner.model.model, algo))
        else:
            logger.error("Pool stats not returned for Pool/Model/Algo {}/{}/{}".format(pool, miner.model.model, algo))


