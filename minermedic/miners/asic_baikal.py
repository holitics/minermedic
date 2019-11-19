# asic_baikal.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.logger import root_logger as logger
from minermedic.miners.base_miner import BaseMiner
from minermedic.miner_results import MinerChipStats
from phenome_core.util import math_functions
from minermedic.api import cgminer
from minermedic.miners.helper import parse_worker_string
from phenome_core.util.network import run_commands_over_ssh

"""

ASIC_BAIKAL 

This inherits from BaseMiner and provides vendor specific 
implementation to retrieve data from all Baikal Miners.

"""

class ASIC_BAIKAL(BaseMiner):

    def __init__(self):
        super(ASIC_BAIKAL, self).__init__()

    def restart(self):

        # use the defaults if not set
        if self.username == "" and self.password == "":
            self.username = "baikal"
            self.password = "baikal"

        # if we can SSH in there, it's a simple "reboot" command,
        # but we must sudo to root so we must send multiple commands

        commands = ['sudo -i', 'reboot']
        return run_commands_over_ssh(self,commands)

    def poll(miner, results):

        global errors
        # Uses SG-MINER 5.6.6
        logger.debug("poll_baikal() - miner=" + str(miner.id))

        # get the DEVICE / CARD stats
        miner_stats = cgminer.get_baikal_devs(miner.ip)

        elapsed_secs = -1

        # if miner STILL not accessible
        status =  miner_stats['STATUS'][0]['STATUS']
        if status == 'error':
            errors = True
            results.inactive_objects.append(miner)

        else:

            worker = ""
            total_mh = 0
            Xs = 0
            Os = 0
            Ds = 0
            Ts = 0

            temps = []
            fan_speeds = []
            elapsed_secs = 0
            total_chips = 0

            pool_name = ""
            algo = ""
            worker = ""
            chips_list = 0

            # Get total number of chips according to miner's model
            # convert miner.model.chips to int list and sum
            try:
                chips_list = [int(y) for y in miner.chips.split(',')]
                Ts = sum(chips_list)
            except:
                if Ts == 0:
                    logger.debug("process_baikal() - miner=" + str(miner.id) + " - chips are EMPTY - check object properties.")

            # Get active pool
            miner_pools = cgminer.get_pools(miner.ip)
            for pool in miner_pools['POOLS']:
                if pool['Stratum Active'] == True:
                    worker = pool['User']
                    algo = pool['Algorithm']
                    #pool_name = pool['Name']
                    # get the PORT as well, different pools/algos at different ports
                    pool_name = pool['URL'].split("//",1)[-1]
                    break

            if algo == "":
                logger.warning("process_baikal() - miner=" + str(miner.id) + " - Miner is IDLE.")
                # increase idle cycles
                miner.idle_cycles_count = miner.idle_cycles_count + 1

            # get the coin address and worker
            coin_address, worker = parse_worker_string(miner, worker)

            # Get other miner stats (temps, chips, etc.)
            for board in miner_stats['DEVS']:

                if board['Enabled']=="Y":

                    # get the total MH
                    board_mh = float(board['MHS 5s'])
                    total_mh = total_mh + board_mh

                    # get the working chips
                    if board['Status']!="Alive" or board_mh == 0:
                        # we have a dead board! need to
                        Xs = Xs + chips_list[0]
                    else:
                        # this board is running
                        elapsed_secs = board['Device Elapsed']
                        Os = Os + chips_list[0]
                        board_temp = board['Temperature']
                        temps.append(board_temp)

            # convert to GigaHashes, since hashrate algo requires that to start
            hashrate_ghs = float(total_mh / 1000)

            # get the chip stats
            chip_stats = MinerChipStats(Os, Xs, Ds, Ts)

            # Get HW Errors
            summary_stats = cgminer.get_summary(miner.ip)

            # process error rate
            hw_error_rate = math_functions.get_formatted_float_rate(summary_stats['SUMMARY'][0]['Device Hardware%'], 4)

            # populate results
            results.populate_miner_results(miner, elapsed_secs, worker, algo, pool_name, chip_stats,
                                           temps, fan_speeds, hashrate_ghs, hw_error_rate)

        return elapsed_secs

