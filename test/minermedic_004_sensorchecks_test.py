# minermedic_004_sensorchecks_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import sys

from test import BaseTest
from minermedic.miner_results import MinerResults
from test.supporting.test_mockobject import MockObject

from minermedic.sensorchecks.chips import ChipCheck
from minermedic.sensorchecks.gpus import GPUCheck
from minermedic.sensorchecks.hashrate import HashCheck

from minermedic.miner_results import MinerChipStats

sys._unit_tests_running = True
sys._unit_tests_use_fake_values = True
sys._unit_tests_load_app_data = True
sys._unit_tests_load_app_meta_data = True
sys._unit_tests_app_name = "minermedic"

CONST_API_PORT = 5000

class TestSensorChecks(BaseTest):

    def setUp(self):

        super(TestSensorChecks, self).setUp()


    def test_001_chips_no_error(self):

        results = MinerResults()
        miner = MockObject()

        # chips_working, chips_defective, chips_missing, chips_total
        chips = MinerChipStats(100, 0, 0, 100)
        results.populate_chip_results(miner, chips)

        args = {"object":miner, "results":results, "error_level": "80%", "warning_level":"90%", "error_timestamp": "last_chip_error_time" }

        check = ChipCheck()
        check.set_arguments(args)

        success = check.execute()
        self.assertEqual(success, True)

        has_chip_error = check.object_states.chip_error
        self.assertEqual(has_chip_error, 0)

    def test_002_chips_has_warning(self):

        results = MinerResults()
        miner = MockObject()

        # chips_working, chips_defective, chips_missing, chips_total
        chips = MinerChipStats(65, 15, 20, 100)
        results.populate_chip_results(miner, chips)

        args = {"object":miner, "results":results, "error_level": "60%", "warning_level":"90%", "error_timestamp": "last_chip_error_time" }

        check = ChipCheck()
        check.set_arguments(args)

        success = check.execute()
        self.assertEqual(success, True)

        has_chip_warning = check.has_warning
        self.assertEqual(has_chip_warning, 1)

    def test_003_chips_has_error(self):

        results = MinerResults()
        miner = MockObject()

        # chips_working, chips_defective, chips_missing, chips_total
        chips = MinerChipStats(40, 40, 20, 100)
        results.populate_chip_results(miner, chips)

        args = {"object":miner, "results":results, "error_level": "60%", "warning_level":"90%", "error_timestamp": "last_chip_error_time" }

        check = ChipCheck()
        check.set_arguments(args)

        success = check.execute()
        self.assertEqual(success, True)

        has_chip_error = check.object_states.chip_error
        self.assertEqual(has_chip_error, 1)

    def test_004_gpus_no_error(self):

        results = MinerResults()
        miner = MockObject()

        # GPUs working, GPUs_defective (no way to tell this - so 0), GPUs not working (IDLE), GPUs total
        chips = MinerChipStats(14, 0, 0, 14)
        results.populate_chip_results(miner, chips)

        args = {"object":miner, "results":results, "error_timestamp": "last_chip_error_time" }

        check = GPUCheck()
        check.set_arguments(args)

        success = check.execute()
        self.assertEqual(success, True)

        has_chip_error = check.object_states.chip_error
        self.assertEqual(has_chip_error, 0)

    def test_005_gpus_has_error(self):

        results = MinerResults()
        miner = MockObject()

        # GPUs working, GPUs_defective (no way to tell this - so 0), GPUs not working (IDLE), GPUs total
        chips = MinerChipStats(12, 0, 2, 14)
        results.populate_chip_results(miner, chips)

        args = {"object":miner, "results":results, "error_timestamp": "last_chip_error_time" }

        check = GPUCheck()
        check.set_arguments(args)

        success = check.execute()
        self.assertEqual(success, True)

        has_chip_error = check.object_states.chip_error
        self.assertEqual(has_chip_error, 1)

    def test_006_hashrates_no_error(self):

        results = MinerResults()
        miner = MockObject()

        algo = 20
        hashrates = {"current":100, "units":"MH/s", "max":105}
        hashrates_by_algo = {algo: {'accepted': 95, 'reported': 100, 'speed_suffix': "MH/s"}}

        results.set_result(miner, "hashrates", hashrates)
        results.set_result(miner, "hashrates_by_algo", hashrates_by_algo)

        args = {"object":miner, "results":results, "error_timestamp": "last_hashrate_error_time", "error_level":"80%", "warning_level":"90%" }

        check = HashCheck()
        check.set_arguments(args)

        success = check.execute()
        self.assertEqual(success, True)

        hashrate_warn = check.has_warning
        self.assertEqual(hashrate_warn, False)

        hashrate_error = check.has_error
        self.assertEqual(hashrate_error, False)

    def test_007_hashrates_warning(self):

        results = MinerResults()
        miner = MockObject()

        algo = 20
        hashrates = {"current":100, "units":"MH/s", "max":105}
        hashrates_by_algo = {algo: {'accepted': 89, 'reported': 0, 'speed_suffix': "MH/s"}}

        results.set_result(miner, "hashrates", hashrates)
        results.set_result(miner, "hashrates_by_algo", hashrates_by_algo)

        args = {"object":miner, "results":results, "error_timestamp": "last_hashrate_error_time", "error_level":"80%", "warning_level":"90%" }

        check = HashCheck()
        check.set_arguments(args)

        success = check.execute()
        self.assertEqual(success, True)

        hashrate_warn = check.has_warning
        self.assertEqual(hashrate_warn, True)

    def test_008_hashrates_error(self):

        results = MinerResults()
        miner = MockObject()

        algo = 20
        hashrates = {"current":79, "units":"MH/s", "max":105}
        hashrates_by_algo = {algo: {'accepted': 75, 'reported': 0, 'speed_suffix': "MH/s"}}

        results.set_result(miner, "hashrates", hashrates)
        results.set_result(miner, "hashrates_by_algo", hashrates_by_algo)

        args = {"object":miner, "results":results, "error_timestamp": "last_hashrate_error_time", "error_level":"80%", "warning_level":"90%" }

        check = HashCheck()
        check.set_arguments(args)

        success = check.execute()
        self.assertEqual(success, True)

        hashrate_error = check.has_error
        self.assertEqual(hashrate_error, True)
