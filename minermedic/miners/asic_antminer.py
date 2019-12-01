# asic_antminer.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from minermedic.miners.base_miner import BaseMiner
from minermedic.miners.helper import get_normalized_gigahash_per_sec_from_hashrate
from minermedic.miner_results import MinerChipStats
from minermedic.api import cgminer

from phenome_core.util import math_functions
from phenome_core.util.network import run_command_over_ssh
from phenome_core.core.base.logger import root_logger as logger

"""

ASIC_ANTMINER 

This inherits from BaseMiner and provides vendor specific
implementation to retrieve data from Antminer Miners.

"""


class ASIC_ANTMINER(BaseMiner):

    def __init__(self):
        super(ASIC_ANTMINER, self).__init__()

    def restart(self):

        # default to NOT trying defaults
        try_using_defaults = False

        # use the defaults if not set
        if self.username == "" and self.password == "":
            self.username = "root"
            self.password = "root"
            try_using_defaults = True

        # if we can SSH in there, it's a simple "reboot" command
        success = run_command_over_ssh(self,'reboot')

        if success is False and try_using_defaults:
            # try one more time with alt creds
            self.username = "root"
            self.password = "admin"
            success = run_command_over_ssh(self,'reboot')
            if success is False:
                # just reset the password so we won't keep trying the defaults
                self.password = ""

        return success

    def poll(miner, results):

        logger.debug("poll_antminer() - miner=" + str(miner.id))

        elapsed_secs = -1
        last_share_time = 0

        # get the miner stats
        miner_stats = cgminer.get_antminer_stats(miner.ip)

        # if miner not accessible, try again!
        if miner_stats['STATUS'][0]['STATUS'] == 'error':
            miner_stats = cgminer.get_antminer_stats(miner.ip)

        # if miner STILL not accessible
        if miner_stats['STATUS'][0]['STATUS'] == 'error':
            results.inactive_objects.append(miner)

        else:

            # WORKER, POOL, ALGO, LAST SHARE TIME

            # retrieve and process the pool stats on the Miner
            miner.poll_pool_stats()

            # CHIPS, FANS, TEMPS

            Os = 0
            Xs = 0
            Ds = 0
            TsC = 0
            temps_chips = []
            temps_pcb = []
            fan_speeds = []
            miner_type = None

            # get total number of chips
            Ts = sum([int(y) for y in str(miner.chips).split(',')])

            try:
                miner_type = miner_stats['STATS'][0]['Type']
            except:
                pass

            # Get ASIC chip, temp, fan, counts, status, etc. all with a single loop
            for key in miner_stats['STATS'][1].keys():

                # FANS

                if "fan_num" in key:
                    # ignore for now
                    pass
                elif "fan" in key:
                    value = miner_stats['STATS'][1][key]
                    if (value>0):
                        fan_speeds.append(value)

                # TEMPS

                if "temp2_" in key:
                    value = miner_stats['STATS'][1][key]
                    if len(temps_chips)>0 and len(temps_pcb)==0:
                        temps_pcb = temps_chips
                        temps_chips = []
                    if (value>0):
                        temps_chips.append(value)
                elif "temp_num" in key:
                    # do not use the number of temps in the aggregate
                    pass
                elif "temp_max" in key:
                    # do not use max values in aggregate
                    # we may use this later!!
                    pass
                elif "temp" in key:
                    value = miner_stats['STATS'][1][key]
                    if (value>0):
                        temps_chips.append(value)

                # CHIPS

                if "chain_acn" in key:
                    value = miner_stats['STATS'][1][key]
                    # not used, but maybe in the future we will use it
                    TsC = TsC + value

                if "chain_acs" in key:
                    value = miner_stats['STATS'][1][key]
                    asic_chips = [value]
                    # good chips
                    O = [str(o).count('o') for o in asic_chips]
                    Os = sum(O) + Os
                    # bad chips
                    X = [str(x).count('x') for x in asic_chips]
                    Xs = sum(X) + Xs
                    # inactive (dash) chips
                    D = [str(x).count('-') for x in asic_chips]
                    Ds = sum(D) + Ds


            # summarize chip stats with an object
            chip_stats = MinerChipStats(Os, Xs, Ds, Ts)

            # HASHRATE

            # what are the hashrate units of this miner?
            hashrate_units = miner.hashrate[0]['units'].upper()
            hashrate = None

            try:
                # Get the current hashrate of the Antminer (usually stored in the 'GH/S 5s' or 'GH/S avg' params
                hashrate = float(str(miner_stats['STATS'][1]['GHS 5s']))
            except:
                pass

            if hashrate is None:
                try:
                    hashrate = float(str(miner_stats['STATS'][1]['MHS 5s']))
                except:
                    pass

            # now, convert to GH/s which is what the normalized result handling requires
            hashrate_ghs = get_normalized_gigahash_per_sec_from_hashrate(hashrate, hashrate_units)

            # Get HW Errors
            hw_error_rate = None

            try:
                hw_error_rate = math_functions.get_formatted_float_rate(miner_stats['STATS'][1]['Device Hardware%'], 4)
            except:
                pass

            if hw_error_rate is None:
                # we can get it from SUMMARY call
                summary_json = cgminer.get_summary(miner.ip)
                try:
                    summary = summary_json['SUMMARY'][0]
                    hw_error_rate = math_functions.get_formatted_float_rate(summary['Device Hardware%'], 4)
                except:
                    pass

            # UPTIME
            elapsed_secs = miner_stats['STATS'][1]['Elapsed']

            # Populate results
            results.populate_miner_results(miner, elapsed_secs, miner.worker, miner.algo, miner.pool, chip_stats,
                                           temps_chips, fan_speeds, hashrate_ghs, hw_error_rate)

        return elapsed_secs
