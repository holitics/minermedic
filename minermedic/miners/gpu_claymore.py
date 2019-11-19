# gpu_claymore.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.util import time_functions, math_functions

from minermedic.constants import _POWER_GPU_CARD_WATTS_DEFAULT
from minermedic.api import cgminer
from minermedic.api.cgminer import restart_claymore_miner
from minermedic.miners.base_miner import BaseMiner
from minermedic.miner_results import MinerChipStats
from minermedic.pools.helper import get_coin_index, get_algo
from minermedic.miners.helper import parse_worker_string, get_normalized_hashrate_from_gigahash_per_sec

from phenome_core.core.base.logger import root_logger as logger

"""

GPU_CLAYMORE

This inherits from BaseMiner and provides vendor specific 
implementation to retrieve data from Claymore GPU Mining Rigs.

"""


class GPU_CLAYMORE(BaseMiner):

    def __init__(self):
        super(GPU_CLAYMORE, self).__init__()

    def get_power_usage_estimate_by_card_count(card_count):

        try:
            from phenome import flask_app
            card_watts = int(flask_app.config.get('POWER_GPU_CARD_WATTS_DEFAULT'))
        except:

            logger.warning("Could not get a configured WATT Power Usage per GPU card. "
                           "Using default of {} Watts per card".format(_POWER_GPU_CARD_WATTS_DEFAULT))

            card_watts = _POWER_GPU_CARD_WATTS_DEFAULT

        # estimate the total watts == the number of GPU cards * watts/per/card + some overhead
        #  for the system and PSUs themselves considering this is probably a GPU rig
        return (card_count * card_watts) + 150

    def process_miner_local_config(miner):

        # We need to get the coin address and worker name
        # This is possible by grabbing the local configuration file from claymore,
        # but only if it's set in config.txt on the server and we have full access

        worker = ""

        if miner.coin_address is not None and len(miner.coin_address) == 0:

            # first set it to None
            miner.coin_address = None
            # assume no issue with retrieving the config file
            had_issue = False

            # TODO - move this section to a new module

            try:
                # try to get it from config.txt file
                filename = 'config.txt'
                config_txt_response = cgminer.get_claymore_configfile(miner.ip, filename)
                if config_txt_response.get('result') is not None:
                    if config_txt_response['result'][0] == filename:
                        config_txt = bytes.fromhex(config_txt_response['result'][1]).decode('utf-8')
                        lines = config_txt.split('\n')
                        for line in lines:
                            if line.startswith('-ewal'):
                                worker = line.split(' ')[1]
                                # get the coin address and worker
                                coin_address, worker = parse_worker_string(miner, worker)
                                miner.coin_address = coin_address
                                miner.worker_name = worker
                                break

                        if coin_address is None and worker is None:
                            had_issue = True

            except:
                had_issue = True

            if had_issue:
                logger.warning("MinerMedic could not automatically retrieve miner "
                               "wallet address from config file ('config.txt'). "
                               "To do this, ensure that the '-ewal' argument is "
                               "not commented and set correctly. "
                               "Otherwise, the coin address and worker name can "
                               "be set manually in the object's configuration.")

    def poll(miner, results):

        logger.debug("poll_etherminer() - miner=" + str(miner.id))

        elapsed_secs = -1

        # get the miner stats
        miner_stats = cgminer.get_claymore_stats(miner.ip)

        # if miner not accessible... add to inactive
        if miner_stats.get('result') is None:
            results.inactive_objects.append(miner)

        else:

            result = miner_stats['result']

            # TODO - to support dual mining, will have to refactor this code
            # and probably call twice, once for each algo

            algo_idx = 0

            # version of claymore and COIN being mined
            version, coin = result[0].split(" - ")

            if coin is not None and len(coin)>0 and coin != miner.hashrate[0]['coin']:
                # coin changed, need to update it
                coin_index = get_coin_index(coin)
                if coin_index>=0:
                    # set the COIN currently being mined
                    miner.hashrate[algo_idx]['coin'] = coin


            # process the local config to get miner coin address and worker name
            GPU_CLAYMORE.process_miner_local_config(miner)

            # Get pool name
            pool = result[7]

            if coin == "ETH" or coin == "ETC" or "ethermine" in pool:
                algo = "ethash"
            else:
                # usually you can get the algo from the pool
                algo = get_algo(pool)

            if miner.hashrate[algo_idx]['algo']!=algo and algo is not None:
                miner.hashrate[algo_idx]['algo'] = algo

            # Get miner's GPU stats
            gpu_hashes_string = result[3]
            gpu_hashes = gpu_hashes_string.split(';')

            # count number of working GPU
            Os = sum([int(x)>0 for x in gpu_hashes])

            # count number of non-working GPUs (does not apply)
            Xs = 0

            # get number of in-active GPUs
            Gi = sum([int(x)==0 for x in gpu_hashes])

            # Get total number of GPUs
            Ts = len(gpu_hashes)

            if Gi==Ts:
                logger.warning("process_claymore() - miner=" + str(miner.id) + " - Miner is IDLE.")
                # increase idle cycles
                miner.idle_cycles_count = miner.idle_cycles_count + 1

            # Get the temperatures of the miner, they are mixed with fan speeds
            temps_and_fans = result[6].split(';')

            # get the temps and convert to ints
            temps = temps_and_fans[::2]
            temps = [int(i) for i in temps]

            # get the fan speeds and convert to ints
            fan_pcts = temps_and_fans[1::2]
            fan_pcts = [int(i) for i in fan_pcts]

            # Get Total Hashrate for Miner (expressed in KH/s from the API)
            eth_stats = result[2].split(';')
            current_hashrate = int(eth_stats[0])

            # Get Gigahashes by converting the KH to GH
            ghs5s = float(int(current_hashrate)/1000000)

            # TODO - revisit with dual mining
            algo_rate = miner.hashrate[algo_idx]['rate']

            if algo_rate is None or algo_rate == 0:
                # get the hashrate in the correct units
                normalized_rate, hashrate_units = get_normalized_hashrate_from_gigahash_per_sec(ghs5s, miner.hashrate[algo_idx]['units'])
                miner.hashrate[algo_idx]['rate'] = normalized_rate

            if miner.power_usage_watts == 0:

                if miner.hashrate[algo_idx]['power'] == 0:
                    # TODO - if this is connected to a PDU, check whether there is Power Management on the PDU
                    # and if it will tell you power usage. If so, use those estimates...
                    # and set miner.power_usage_watts = XXX
                    # If not...
                    pass

                if miner.power_usage_watts == 0:
                    # estimate power usage based on card count and default GPU card power usage setting
                    # FALLBACK TO CONFIG AND DEFAULTS
                    miner.power_usage_watts = GPU_CLAYMORE.get_power_usage_estimate_by_card_count(Ts)

            eth_shares_good = int(eth_stats[1])
            eth_shares_stale = int(eth_stats[2])
            eth_shares_invalid = int(result[8].split(';')[0])
            eth_shares_total = eth_shares_good + eth_shares_stale + eth_shares_invalid

            hw_error_rate_raw = ((eth_shares_stale + eth_shares_invalid) / eth_shares_total) * 100
            hw_error_rate = math_functions.get_formatted_float_rate(hw_error_rate_raw, 4)

            # Get uptime
            elapsed_secs = int(result[1]) * 60

            chip_stats = MinerChipStats(Os, Xs, Gi, Ts)

            results.populate_miner_results(miner, elapsed_secs, miner.worker_name, algo, pool, chip_stats,
                                           temps, fan_pcts, ghs5s, hw_error_rate)

            if (Gi>0):
                # some special debug for GPU miner issues
                logger.debug("Missing {} GPUs in miner {}, stats={}".format(Gi, miner.ip, gpu_hashes_string))

        return elapsed_secs

    def restart(self):

        millis = time_functions.current_milli_time()

        if (millis - self.restart_delay) > self.last_restart_time:
            # we have not tried to restart in a while...
            self.last_restart_time = millis
            response = restart_claymore_miner(self.ip)

        # did the restart fail?
        restart_failed = response is None or response['STATUS'][0]['STATUS'] == 'error'

        return not restart_failed

