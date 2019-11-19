# asic_avalonminer.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from minermedic.miners.base_miner import BaseMiner
from minermedic.miners.helper import parse_worker_string, get_normalized_gigahash_per_sec_from_hashrate
from minermedic.miner_results import MinerChipStats
from minermedic.api import cgminer
from minermedic.pools.helper import get_algo

from phenome_core.util import math_functions
from phenome_core.core.base.logger import root_logger as logger
from phenome_core.util.time_functions import get_total_minutes_seconds_from_timestamp, current_milli_time
from phenome_core.core.database.model.api import get_object_by_unique_id, create_object

"""

ASIC_AVALONMINER 

This inherits from BaseMiner and provides vendor specific 
implementation to retrieve data from Avalon Miners.

"""

class ASIC_AVALONMINER(BaseMiner):

    def __init__(self):
        super(ASIC_AVALONMINER, self).__init__()

    def restart(self):

        # TODO - implement restart for Avalon Miners
        return False

    def poll(miner, results):

        logger.debug("poll_avalonminer() - miner=" + str(miner.id))

        elapsed_secs = -1
        last_valid_work = 0

        if hasattr(miner, 'last_poll_time'):
            last_poll_time = miner.last_poll_time
            if ((current_milli_time() - last_poll_time) < 60000):
                # Do not poll it again, we handle all miners on the controller during the poll phase
                return True

        miners = []
        miners_info = []

        # get the miner stats
        miner_stats = cgminer.get_avalon_stats(miner.ip)

        # if miner not accessible
        if miner_stats['STATUS'][0]['STATUS'] is not 'S':
            results.inactive_objects.append(miner)
            return elapsed_secs

        # controller elapsed seconds
        elapsed_secs = miner_stats['STATS'][0]['Elapsed']

        # assuming all is good, get the devs and pools
        miner_stats_devs = cgminer.get_avalon_devs(miner.ip)
        miner_pools = cgminer.get_pools(miner.ip)

        # basic pool processing
        for miner_pool in miner_pools['POOLS']:
            miner_pool_status = miner_pool.get('Status')
            miner_pool_stratum_active = miner_pool.get('Stratum Active')

            if (miner_pool_status is not None and miner_pool_status == "Alive") or (miner_pool_stratum_active is not None and miner_pool_stratum_active == True):
                # pull pertinent information
                worker = miner_pool['User']
                # get the PORT as well, different pools/algos at different ports
                pool = miner_pool['URL'].split("//",1)[-1]
                algo = get_algo(pool)
                break

        if (algo is None):
            algo = miner.hashrate[0]['algo']

        # get the coin address and worker
        coin_address, worker = parse_worker_string(miner, worker)


        # get all miner info for each miner
        # it is possible to have 20 miners, 5 miners per AUC per controller
        for i in range(20):
            try:
                miner_info = miner_stats['STATS'][0]['MM ID' + str(i+1)]
                # this returns a chunky string for each device like:

                # "Ver[7411706-3162860] DNA[013cae6bfb1bb6c6] Elapsed[183] MW[2024 2024 2024 2002] LW[8074]
                #  MH[3 0 3 4] HW[10] DH[0.000%] Temp[38] TMax[93] Fan[4110] FanR[48%] Vi[1215 1215 1211 1210]
                #  Vo[4461 4447 4438 4438] GHSmm[7078.84] WU[88583.15] Freq[628.45] PG[15] Led[0]
                #  MW0[6 3 8 7 5 10 4 5 6 7 12 4 7 9 6 11 11 9 11 9 7 4] MW1[3 5 9 8 7 4 4 4 6 5 9 3 8 4 8 8 7 5 6 8 4 4]
                #  MW2[12 7 3 4 5 4 5 2 6 6 11 6 6 6 7 5 5 9 4 6 6 5] MW3[5 3 11 5 5 5 4 6 8 6 3 7 3 8 4 9 4 7 7 3 5 3]
                #  TA[88] ECHU[16 0 0 0] ECMM[0] FM[1] CRC[0 0 0 0] PAIRS[0 0 0] PVT_T[21-76/1-88/83 1-80/11-92/84 21-82/12-93/83 1-82/10-93/87]"

                # check out page 13 for a detailed explanation: https://canaan.io/wp-content/uploads/2018/05/Troubleshooting-and-repair-guide-for-AvalonMiner-models-721-741-761-821-and-841-release-v1.4-14.05.2018.pdf

                if miner_info is not None:
                    miner_info = miner_info + " _NULL_[1"  # add _NULL_ in order to split correctly
                    miners_info.append(dict(x.split('[') for x in miner_info.split('] ')))
            except:
                pass

        # Now we have info on all the miners attached to this Avalon/AUC3 controller
        # Iterate through and process

        miner_int_id = 0
        miner_is_controller = False
        controller_ver = ''

        for info in miners_info:

            temps_chips = []
            fan_speeds = []
            device_hashrate_1_min = None

            # get the miner ID
            controller_ver = info.get('Ver')[:3]
            dna = info.get('DNA')
            miner_unique_id = "Avalon_" + controller_ver + " " + dna

            # does this miner exist?
            mi = get_object_by_unique_id(miner_unique_id)
            if mi is None:
                if miner.unique_id == miner.ip:
                    # later we will delete the CONTROLLER
                    miner_is_controller = True

                mi = create_object(miner.model_id,miner.ip,dna,miner_unique_id)

            if mi is not None:
                miners.append(mi)
                # set the last poll time
                mi.last_poll_time = current_milli_time()

            # get detailed HW info
            fan_speeds.append(int(info.get('Fan')))
            temp_intake = int(info.get('Temp'))
            temp_chips_max = int(info.get('TMax'))
            temps_chips.append(temp_chips_max)
            hw_errors = int(info.get('HW'))
            hashrate = info.get('GHSmm')
            total_working_chips = int(info.get('TA'))

            mcl = mi.chips.split(',')
            total_miner_chips = sum([int(i) for i in mcl if type(i) == int or i.isdigit()])

            missing_chips = total_miner_chips - total_working_chips
            chip_stats = MinerChipStats(total_working_chips, 0, missing_chips, total_miner_chips)
            hw_error_rate_calc = (hw_errors / total_miner_chips) * 100

            try:
                if info.get('PVT_T0') is not None:
                    temps_chips.extend(info.get('PVT_T0').split(','))
                    temps_chips.extend(info.get('PVT_T1').split(','))
                    temps_chips.extend(info.get('PVT_T2').split(','))
                    temps_chips.extend(info.get('PVT_T3').split(','))
                    # finally convert these strings to ints
                    temps_chips = list(map(int, temps_chips))
            except:
                pass

            devs = miner_stats_devs['DEVS']
            for dev in devs:
                if dev['ID'] == miner_int_id:

                    # we can get lots of specific work and device info here
                    last_valid_work = dev.get('Last Valid Work')

                    # should we use our calculated hw_error_rate (above) or get direct from DEVs
                    hw_error_rate_direct = dev.get('Device Hardware%')

                    # maybe useful in the future
                    device_status = dev.get('Status')

                    # use the 1M, it is more accurate than the above average
                    hashrate = dev.get('MHS 1m') / 1000 # convert to GHS

                    shares_accepted = dev.get('Accepted')

                    # Device Uptime
                    elapsed_secs = dev.get('Device Elapsed')

                    # Determine IDLE STATE
                    if last_valid_work is not None:

                        # convert last share time to minutes (i.e. share cycles) and then compare and set if needed
                        last_share_minutes, last_share_seconds = get_total_minutes_seconds_from_timestamp(last_valid_work)

                        # Seeing a situation where LastValidWork is not getting updated. Maybe a version issue.
                        # also adding a shares or 1-minute hashrate check

                        if last_share_minutes >= 1 and (hashrate==0 or shares_accepted==0):
                            logger.debug("process_avalonminer() - miner=" + str(mi.id) + " - Miner is IDLE.")
                            mi.idle_cycles_count = mi.idle_cycles_count + 1
                        elif mi.idle_cycles_count > 1:
                            # reset it
                            mi.idle_cycles_count = 0

                    break

            # what are the hashrate units of this miner?
            hashrate_units = mi.hashrate[0]['units'].upper()

            try:
                # now, convert to GH/s which is what the normalized result handling requires
                hashrate_ghs = get_normalized_gigahash_per_sec_from_hashrate(hashrate, hashrate_units)
            except:
                pass

            try:
                hw_error_rate = math_functions.get_formatted_float_rate(hw_error_rate_direct, 4)
            except:
                hw_error_rate = math_functions.get_formatted_float_rate(hw_error_rate_calc, 4)

            # Populate results FOR THIS MINER
            results.populate_miner_results(mi, elapsed_secs, worker, algo, pool, chip_stats,
                                           temps_chips, fan_speeds, hashrate_ghs, hw_error_rate)

            # increment the miner_int_id
            miner_int_id = miner_int_id + 1

        if miner_is_controller:
            miner.unique_id = "Avalon Controller " + controller_ver + " " + miner.ip
            miner.set_enabled(False)

        return elapsed_secs
