# asic_innosilicon.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from minermedic.miners.base_miner import BaseMiner
from minermedic.miners.helper import get_normalized_gigahash_per_sec_from_hashrate
from minermedic.miner_results import MinerChipStats
from minermedic.api import cgminer

from phenome_core.util import math_functions
from phenome_core.core.base.logger import root_logger as logger

"""

ASIC_INNOSILICON

This inherits from BaseMiner and provides vendor specific
implementation to retrieve data from Innosilicon Miners.

"""


class ASIC_INNOSILICON(BaseMiner):

    def __init__(self):
        super(ASIC_INNOSILICON, self).__init__()

    def poll(miner, results):

        logger.debug("poll_innosilicon() - miner=" + str(miner.id))

        elapsed_secs = -1
        last_share_time = 0

        # get the miner stats
        miner_stats = cgminer.get_cgminer_stats(miner.ip)

        # if miner not accessible
        if miner_stats['STATUS'][0]['STATUS'] == 'error':
            results.inactive_objects.append(miner)

        else:

            # retrieve and process the pool stats on the Miner
            miner.poll_pool_stats()

            # CHIPS, FANS, TEMPS

            Os = 0
            Xs = 0
            Ds = 0
            temps_chips = []
            fan_speeds = []

            # get total number of chips per board
            chips_per_board = int(miner.chips.split(',')[0])
            boards = 0

            for board in miner_stats['STATS']:

                # Get ASIC chip, temp, fan, counts, status, etc. all with a single loop
                for key in board.keys():

                    # BOARD COUNT
                    if key == "ID":
                        value = board[key]
                        if 'BA' in value:
                            boards = boards + 1

                    # TEMPS
                    if "TEMP(AVG)" in key:
                        value = board[key]
                        if (value > 0):
                            temps_chips.append(value)

                    # CHIPS

                    if "ASIC" in key:
                        value = board[key]
                        # good chips
                        Os = Os + value
                        # bad chips
                        Xs = Xs - (chips_per_board-value)

            Ts = boards * chips_per_board

            # summarize chip stats with an object
            chip_stats = MinerChipStats(Os, Xs, Ds, Ts)

            # HASHRATE

            # what are the hashrate units of this miner?
            hashrate_units = miner.hashrate[0]['units'].upper()
            hashrate_pool = None

            summary = cgminer.get_summary(miner.ip)['SUMMARY'][0]

            try:
                # Get the current hashrate
                hashrate_pool = float(str(summary['GHS 5s']))
            except:
                pass

            if hashrate_pool is None:
                # try for older MHS
                try:
                    hashrate_pool = float(str(summary['MHS 5s']))
                except:
                    pass

            # now, convert to GH/s which is what the normalized result handling requires
            hashrate_pool_ghs = get_normalized_gigahash_per_sec_from_hashrate(hashrate_pool, hashrate_units)

            # get the total possible hashrate by multiplying base board hashrate
            # by number of boards being reported by the miner controller
            hashrate_miner = int(miner.hashrate[0]['rate'] * boards)

            # set the override total hashrate for this miner
            results.set_miner_hashrate_override(miner, hashrate_miner)

            try:
                hw_error_rate = math_functions.get_formatted_float_rate(summary['Device Hardware%'], 4)
            except:
                pass

            # UPTIME
            elapsed_secs = miner_stats['STATS'][0]['Elapsed']

            # Populate results
            results.populate_miner_results(miner, elapsed_secs, miner.worker, miner.algo, miner.pool, chip_stats,
                                           temps_chips, fan_speeds, hashrate_pool_ghs, hw_error_rate)

        return elapsed_secs

