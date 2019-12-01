
# minermedic_002_mining_pools_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import sys

from phenome.test import BaseTest
from phenome.test.supporting.test_mockobject import MockObject
from minermedic.pools.helper import process_pool_apis
from minermedic.miner_results import MinerResults
from phenome import flask_app
from phenome_core.core.base.logger import root_logger as logger
from phenome_core.core.database.model.api import get_objectmodel_by_name

sys._unit_tests_running = True
sys._unit_tests_use_fake_values = True
sys._unit_tests_load_app_data = True
sys._unit_tests_load_app_meta_data = True
sys._unit_tests_app_name = "minermedic"


class TestMiningPools(BaseTest):

    def setUp(self):

        super(TestMiningPools, self).setUp()

    def _test_mining_pool(self, watts, coin_address, worker, algo, hashrate_by_algo,
                          pool, sim_urls, sim_file, miner_model_id):

        algo_id = 0
        hashrate = None
        profitability = None

        results = MinerResults()
        miner = MockObject()

        if miner_model_id is not None:
            miner.model = get_objectmodel_by_name(miner_model_id)

        # use an arbitrary number for our power so we can get profitability numbers
        miner.power_usage_watts = watts

        # coin address is needed to query for ethermine stats
        miner.coin_address = coin_address

        worker = worker
        algo = algo
        pool = pool

        # tell the REST API which URLS to simulate, which port to target
        sys._unit_tests_API_SIMULATE_URLS = sim_urls
        sys._unit_tests_API_TARGET_LOC = self.CONST_SIMULATOR_API_TARGET_LOC
        sys._unit_tests_API_TARGET_PORT = self.CONST_SIMULATOR_API_TARGET_PORT

        # do the POOL API and HASHRATE calls
        sys._unit_tests_MINERMEDIC_CALL_POOL_APIS = True
        sys._unit_tests_MINERMEDIC_CALL_HASHRATE_CALCS = True

        # start simulator

        # get path to data file
        simulator_data_path = self.absolute_path_of_test_directory + "/apps/minermedic/resources/mining_pools/" + sim_file

        # start the simulator
        simulator = self.startSimulator(simulator_data_path, 'HTTP', str(self.CONST_SIMULATOR_API_TARGET_PORT))

        try:

            # contact pools, do profitability stuff
            process_pool_apis(results, miner, worker, algo, pool)

            # get the resulting "algo_idx"
            algo_id = results.get_result(miner.id, 'algo')

            # get the accepted hashrate from the POOL
            hashrate = results.get_result(miner.id, 'hashrates_by_algo')[hashrate_by_algo]['accepted']

            profitability = results.get_result(miner.id, 'profitability')

        except Exception as ex:
            logger.error(ex)

        finally:
            simulator.stop()

        # return the results
        return algo_id, hashrate, profitability

    def test_001_mining_pool_hub(self):

        # set the needed API and USER_ID keys
        flask_app.config['MINING_POOL_HUB_API_KEY'] = 'af3770711a5bbeed369699c1a0ca793cb2ab8ef49d9ca0d4896eac344f9fffff'
        flask_app.config['MINING_POOL_HUB_USER_ID'] = '123456'

        watts = 800
        worker = "worker1"
        coin_address = None
        algo_in = "myriadcoin-groestl"
        algo_out = 'Myriad-Groestl'
        pool = "hub.miningpoolhub.com:17005"
        sim_urls = ["(.*)(miningpoolhub.com)","(min-api.cryptocompare.com)"]
        sim_file = "miningpoolhub.py"

        algo_id, hashrate, profitability = \
            self._test_mining_pool(watts, coin_address, worker, algo_in, algo_out, pool, sim_urls, sim_file, None)

        # now do the tests
        self.assertEqual(algo_id, 100)
        self.assertEqual(hashrate, 10.536986433000001)
        self.assertEqual(profitability, 0.24463984606636374)

    def test_002_nicehash(self):

        watts = 800
        worker = "worker1"
        coin_address = '1J6HNskoH271PVPFvfAmBqUmarMFjwwAAA'
        algo_in = "lbry"
        algo_out = 'lbry'
        pool = "lbry.usa.nicehash.com:3356"
        sim_urls = ["(.*)(nicehash.com)","(min-api.cryptocompare.com)"]
        sim_file = "nicehash.py"

        # for NICEHASH we need to pull the speed information off of the model configuration
        model_id = "ASIC_Baikal_GIANT_B"

        algo_id, hashrate, profitability = \
            self._test_mining_pool(watts, coin_address, worker, algo_in, algo_out, pool, sim_urls, sim_file, model_id)

        # now do the tests
        self.assertEqual(algo_id, 23)
        self.assertEqual(hashrate, 37.04807992343783)
        self.assertEqual(profitability, 0.015007162499999997)

    def test_003_ethermine_eth(self):

        watts = 800
        sim_urls = ["(.*)(.ethermine.org)","(min-api.cryptocompare.com)"]
        sim_file = "ethermine_eth.py"
        coin_address = '0x41daf079cdefa7800eab2e51748614f0d386b1ff'
        worker = "4814F8FF882B"
        algo_in = "ethash"
        algo_out = "ethash"
        pool = "us1.ethermine.org:4444"

        algo_id, hashrate, profitability = \
            self._test_mining_pool(watts, coin_address, worker, algo_in, algo_out, pool, sim_urls, sim_file, None)

        # now do the tests
        self.assertEqual(algo_id, 20)
        self.assertEqual(hashrate, 35555555.55555555)
        self.assertEqual(profitability, 0.06844435263755579)

    def test_004_ethermine_etc(self):

        watts = 800
        sim_urls = ["(.*)(.ethermine.org)","(min-api.cryptocompare.com)"]
        sim_file = "ethermine_etc.py"
        coin_address = '0x2da4e946c0ee6977bc44fbba9019b3931952cfff'
        worker = "holitics1"
        algo_in = "ethash"
        algo_out = "ethash"
        pool = "us1-etc.ethermine.org:14444"

        algo_id, hashrate, profitability = \
            self._test_mining_pool(watts, coin_address, worker, algo_in, algo_out, pool, sim_urls, sim_file, None)

        # now do the tests
        self.assertEqual(algo_id, 20)
        self.assertEqual(hashrate, 188888888.8888889)
        self.assertEqual(profitability, 0.37976668267087954)

    def test_005_f2pool(self):

        watts = 800
        sim_urls = ["(.*)(.f2pool.com)(.*)","(min-api.cryptocompare.com)"]
        sim_file = "f2pool.py"
        coin_address = 'holitics'
        worker = "001"
        algo_in = "scrypt"
        algo_out = "scrypt"
        pool = "ltc-us.f2pool.com:8888"

        algo_id, hashrate, profitability = \
            self._test_mining_pool(watts, coin_address, worker, algo_in, algo_out, pool, sim_urls, sim_file, None)

        # now do the tests
        self.assertEqual(algo_id, 0)
        self.assertEqual(hashrate, 0.272014595)
        self.assertEqual(profitability, 0.7613440161264865)



