# minermedic_003_miners_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import sys, time

from test import BaseTest
from minermedic.miner_results import MinerResults
from phenome_core.core.database.model.api import create_temporary_object, get_object_by_unique_id
from phenome_core.core.base.logger import root_logger as logger
from phenome_core.core.database.db import db_session

sys._unit_tests_running = True
sys._unit_tests_use_fake_values = True
sys._unit_tests_load_app_data = True
sys._unit_tests_load_app_meta_data = True
sys._unit_tests_app_name = "minermedic"

CONST_API_PORT = 5000

class TestMiners(BaseTest):

    def setUp(self):

        global CONST_API_PORT
        # increment the port
        CONST_API_PORT = CONST_API_PORT + 1

        # set the port
        self.api_port = CONST_API_PORT

        super(TestMiners, self).setUp()

        # start with the base port, we will need to increment for each test as the sockets take a while to clear up
        sys._unit_tests_API_TARGET_PORT = self.CONST_SIMULATOR_API_TARGET_PORT

    def _test_miner(self, model_id, miner_class, sim_urls, sim_file, alt_miner_unique_id = None):

        # clear any funkiness that could be going on with the DB session, since we are using temp objects, etc.
        db_session.rollback()

        # create a results object
        results = MinerResults()

        test_miner_unique_id = "UNIT_TEST_" + model_id

        # if for some reason it is in there...
        miner = get_object_by_unique_id(test_miner_unique_id)
        if miner is None:
            # create the miner
            miner = create_temporary_object(model_id, "127.0.0.1", "FF:FF:FF:FF:FF:FF", test_miner_unique_id)

        # store the ID for deletion later
        test_miner_id = miner.id
        results_miner_id = test_miner_id

        fan_speeds = None
        temperature = None
        hw_error_rates = None
        miner_chips = None
        uptime = None

        # tell the REST API which URLS to simulate, which port to target
        sys._unit_tests_API_SIMULATE_URLS = sim_urls
        sys._unit_tests_API_TARGET_LOC = self.CONST_SIMULATOR_API_TARGET_LOC
        sys._unit_tests_API_TARGET_PORT = self.api_port

        # skip the POOL API and HASHRATE calls
        sys._unit_tests_MINERMEDIC_CALL_POOL_APIS = False
        sys._unit_tests_MINERMEDIC_CALL_HASHRATE_CALCS = False

        # start simulator

        # get path to data file
        simulator_data_path = self.absolute_path_of_test_directory + "/apps/minermedic/resources/miners/" + sim_file

        # start the simulator
        simulator = self.startSimulator(simulator_data_path, 'JSON_RPC', self.api_port)

        try:

            miner_class.poll(miner,results)

            if alt_miner_unique_id is not None:
                # specify another Miner ID to get the results for
                alt_miner = get_object_by_unique_id(alt_miner_unique_id)
                alt_miner_id = alt_miner.id
                results_miner_id = alt_miner_id

            fan_speeds = results.get_result(results_miner_id, 'fan_speeds_avg')
            temperature = results.get_result(results_miner_id, 'temperature')
            hw_error_rates = results.get_result(results_miner_id, 'hw_error_rates')
            miner_chips = results.get_result(results_miner_id, 'miner_chips')
            uptime = results.get_result(results_miner_id, 'uptimes')

        except Exception as ex:
            logger.error(ex)

        finally:

            try:
                simulator.stop()
                time.sleep(2)
            except:
                pass

        # return the results
        return fan_speeds, temperature, hw_error_rates, miner_chips, uptime

    def test_001_miner_CLAYMORE(self):

        from minermedic.miners.gpu_claymore import GPU_CLAYMORE

        model_id = "GPU_Claymore"
        sim_file = "claymore_gpu.py"

        fan_speeds, temperature, hw_error_rates, miner_chips, uptime = \
            self._test_miner(model_id, GPU_CLAYMORE, None, sim_file)

        # now do the tests
        self.assertEqual(fan_speeds, '80%')
        self.assertEqual(temperature, 55)
        self.assertEqual(hw_error_rates, '0.0')
        self.assertEqual(miner_chips['total'], 12)
        self.assertEqual(str(uptime), '0:31:00')


    def test_002_miner_BAIKAL_GIANT_N(self):

        from minermedic.miners.asic_baikal import ASIC_BAIKAL

        model_id = "ASIC_Baikal_GIANT_N+"
        sim_file = "baikal_giant_n.py"

        fan_speeds, temperature, hw_error_rates, miner_chips, uptime = \
            self._test_miner(model_id, ASIC_BAIKAL, None, sim_file)

        # now do the tests
        self.assertEqual(fan_speeds, '')
        self.assertEqual(temperature, 29)
        self.assertEqual(hw_error_rates, '0.0')
        self.assertEqual(miner_chips['total'], 192)
        self.assertEqual(str(uptime), '0:22:29')


    def test_003_miner_BAIKAL_GIANT_B(self):

        from minermedic.miners.asic_baikal import ASIC_BAIKAL

        model_id = "ASIC_Baikal_GIANT_B"
        sim_file = "baikal_giant_b.py"

        fan_speeds, temperature, hw_error_rates, miner_chips, uptime = \
            self._test_miner(model_id, ASIC_BAIKAL, None, sim_file)

        # now do the tests
        self.assertEqual(fan_speeds, '')
        self.assertEqual(temperature, 41)
        self.assertEqual(hw_error_rates, '0.0')
        self.assertEqual(miner_chips['total'], 192)
        self.assertEqual(str(uptime), '2 days, 19:22:39')


    def test_004_miner_BAIKAL_X10(self):

        from minermedic.miners.asic_baikal import ASIC_BAIKAL

        model_id = "ASIC_Baikal_GIANT_X10"
        sim_file = "baikal_giant_x10.py"

        fan_speeds, temperature, hw_error_rates, miner_chips, uptime = \
            self._test_miner(model_id, ASIC_BAIKAL, None, sim_file)

        # now do the tests
        self.assertEqual(fan_speeds, '')
        self.assertEqual(temperature, 22)
        self.assertEqual(hw_error_rates, '0.0')
        self.assertEqual(miner_chips['total'], 192)
        self.assertEqual(str(uptime), '0:09:22')


    def test_005_miner_ANTMINER_E3(self):

        from minermedic.miners.asic_antminer import ASIC_ANTMINER

        model_id = "ASIC_AntMiner_E3"
        sim_file = "antminer_e3.py"

        fan_speeds, temperature, hw_error_rates, miner_chips, uptime = \
            self._test_miner(model_id, ASIC_ANTMINER, None, sim_file)

        # now do the tests
        self.assertEqual(fan_speeds, 2640)
        self.assertEqual(temperature, 46)
        self.assertEqual(hw_error_rates, '0.2171')
        self.assertEqual(miner_chips['total'], 18)
        self.assertEqual(str(uptime), '0:26:31')


    def test_006_miner_ANTMINER_S9(self):

        from minermedic.miners.asic_antminer import ASIC_ANTMINER

        model_id = "ASIC_AntMiner_S9"
        sim_file = "antminer_s9.py"

        fan_speeds, temperature, hw_error_rates, miner_chips, uptime = \
            self._test_miner(model_id, ASIC_ANTMINER, None, sim_file)

        # now do the tests
        self.assertEqual(fan_speeds, 5820)
        self.assertEqual(temperature, 75)
        self.assertEqual(hw_error_rates, '0.0')
        self.assertEqual(miner_chips['total'], 189)
        self.assertEqual(str(uptime), '0:04:08')


    def test_007_miner_ANTMINER_L3_P(self):

        from minermedic.miners.asic_antminer import ASIC_ANTMINER

        model_id = "ASIC_AntMiner_L3+"
        sim_file = "antminer_l3_p.py"

        fan_speeds, temperature, hw_error_rates, miner_chips, uptime = \
            self._test_miner(model_id, ASIC_ANTMINER, None, sim_file)

        # now do the tests
        self.assertEqual(fan_speeds, 6075)
        self.assertEqual(temperature, 53)
        self.assertEqual(hw_error_rates, '0.0')
        self.assertEqual(miner_chips['total'], 288)
        self.assertEqual(str(uptime), '0:07:48')

    def test_008_miner_ANTMINER_D3(self):

        from minermedic.miners.asic_antminer import ASIC_ANTMINER

        model_id = "ASIC_AntMiner_D3"
        sim_file = "antminer_d3.py"

        fan_speeds, temperature, hw_error_rates, miner_chips, uptime = \
            self._test_miner(model_id, ASIC_ANTMINER, None, sim_file)

        # now do the tests
        self.assertEqual(fan_speeds, 4360)
        self.assertEqual(temperature, 63)
        self.assertEqual(hw_error_rates, '0.1412')
        self.assertEqual(miner_chips['total'], 180)
        self.assertEqual(str(uptime), '1 day, 9:32:39')


    def test_009_miner_ANTMINER_A3(self):
        # TODO - get dump of the A3 and implement
        pass

    def test_010_miner_WHATSMINER(self):
        pass

    def test_011_miner_CANAAN_AVALON_7XX(self):

        from minermedic.miners.asic_avalonminer import ASIC_AVALONMINER

        model_id = "ASIC_Avalon_V7"
        sim_file = "avalon_741.py"

        # The particular MINER we will be testing results for
        miner_unique_ID = 'Avalon_741 013cae6bfb1bb6c6'

        # PRE-CREATE the miner that will be created by the Avalon code
        miner = create_temporary_object(model_id, "127.0.0.1", "FF:FF:FF:FF:FF:FF", miner_unique_ID)

        fan_speeds, temperature, hw_error_rates, miner_chips, uptime = \
            self._test_miner(model_id, ASIC_AVALONMINER, None, sim_file, miner_unique_ID)

        # now do the tests
        self.assertEqual(fan_speeds, 4110)
        self.assertEqual(temperature, 93)
        self.assertEqual(hw_error_rates, '0.0037')
        self.assertEqual(miner_chips['active'], 88)
        self.assertEqual(str(uptime), '0:02:59')


    def test_012_miner_INNOSILICON_A4(self):
        pass
