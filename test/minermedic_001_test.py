# minermedic_001_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import sys
from test import BaseTest
from phenome_core.core.globals import global_enums
from minermedic.miners.helper import get_normalized_hashrate_from_gigahash_per_sec
from phenome_core.core.database.model.api import get_default_propertyvalues_by_classtype_and_property
from phenome_core.core.constants import _MODEL_CLASSTYPES_TAG_

sys._unit_tests_running = True
sys._unit_tests_use_fake_values = True
sys._unit_tests_load_app_data = True
sys._unit_tests_load_app_meta_data = True
sys._unit_tests_app_name = "minermedic"

# only needed on test 001 for each APP
sys._unit_tests_load_app_data = True
sys._unit_tests_load_app_meta_data = True
sys._unit_tests_loaded_app_meta_data = False


# This TestMetaData can be used on each APP Specific Unit Test File
class TestMetaData(BaseTest):

    def setUp(self):
        super(TestMetaData, self).setUp()

    def test_metadata_001_app_json(self):
        self._test_metadata(sys._unit_tests_app_name + ".json", True)

    def test_metadata_002_app_json_enum_collision(self):
        self._test_enum_collisions(sys._unit_tests_app_name + ".json", True)


class TestMinerMedic(BaseTest):

    def setUp(self):

        super(TestMinerMedic, self).setUp()

    def test_model_001_get_propertymodels_by_classtype_and_property(self):

        # get the model types defined in the global custom enums
        model_types = global_enums.get_enum(_MODEL_CLASSTYPES_TAG_)

        def_props = get_default_propertyvalues_by_classtype_and_property('CRYPTO_MINER','hashrate')
        self.assertGreater(len(def_props), 2)

    def test_model_002_get_propertymodels_by_classtype_and_property_negative(self):

        def_props = get_default_propertyvalues_by_classtype_and_property('CRYPTO_MINER','property_that_does_not_exist')
        self.assertTrue(def_props is None or len(def_props)==0)

    def test_functions_003_normalized_hashrate_calculations_001(self):

        hashrate_ghs5s = 10
        hashrate_info = {"algo": "scrypt", "coin": "litecoin", "rate": 250, "units": "MH/s", "power": 800}

        current_hashrate, hashrate_units = get_normalized_hashrate_from_gigahash_per_sec(hashrate_ghs5s, hashrate_info['units'])
        self.assertTrue(current_hashrate == hashrate_ghs5s*1000)

        current_hashrate, hashrate_units = get_normalized_hashrate_from_gigahash_per_sec(hashrate_ghs5s, "KH/s")
        self.assertTrue(current_hashrate == hashrate_ghs5s * 1000*1000)

        current_hashrate, hashrate_units = get_normalized_hashrate_from_gigahash_per_sec(hashrate_ghs5s, "H/s")
        self.assertTrue(current_hashrate == hashrate_ghs5s * 1000 * 1000 * 1000)
