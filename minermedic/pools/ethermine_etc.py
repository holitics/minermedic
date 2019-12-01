# ethermine_etc.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from minermedic.pools.ethermine import EtherminePool

"""

    EthermineETCPool, based on EtherminePool.

    This is the Pool API for Ethermine ETC.
    SEE: https://etc.ethermine.org/api/pool

    All the code is the same except the COIN and URLs are different.

"""


class EthermineETCPool(EtherminePool):

    # PER WORKER
    _MINER_URL_PER_WORKER = "https://api-etc.ethermine.org/miner/:{MINER}/worker/:{WORKER}/currentStats"

    # PER MINER
    _MINER_URL_PER_MINER = "https://api-etc.ethermine.org/miner/:{MINER}/currentStats"

    # with Ethermine ETC, coin is ETC
    _DEFAULT_COIN_ = "ETC"
