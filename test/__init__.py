# __init__.py (Unit Tests), Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import os, sys, unittest, time, json
from test.core_constants import *

sys._unit_tests_running = True
sys._unit_tests_use_fake_values = True
sys._unit_tests_load_app_data = False
sys._unit_tests_loaded_system_data = False
sys._unit_tests_loaded_unit_test_data = False
sys._unit_tests_load_app_meta_data = False
sys._unit_tests_loaded_app_meta_data = False
sys._unit_tests_app_name = ""

# import the main phenome
from phenome_core.core.database.db import db_session
from phenome_core.core.database.create import CreateDB
from sqlalchemy.orm.dependency import DependencyProcessor


# noinspection PyPackageRequirements
class BaseTest(unittest.TestCase):

    CONST_SIMULATOR_API_TARGET_PORT = 5000
    CONST_SIMULATOR_API_TARGET_LOC = "0.0.0.0"
    CONST_TEST_SENSOR_IP = CONST_TEST_IPADDRESS
    CONST_TEST_SENSOR_MAC = CONST_TEST_MACADDRESS
    CONST_TEST_PDU_IP = CONST_TEST_IPADDRESS_2
    CONST_TEST_PDU_MAC = CONST_TEST_MACADDRESS_2

    def _load_metadata(self, json_file, use_app_metadata_dir=False):

        json_data = None

        if use_app_metadata_dir:
            file = self.app_metadata_directory + json_file
        else:
            file = self.metadirectory + json_file

        from pathlib import Path
        my_file = Path(file)
        if my_file.is_file():
            text_from_file = open(file).read()
            try:
                json_data = json.loads(text_from_file)
            except ValueError:
                pass

        return json_data

    def _test_metadata(self, json_file, use_app_metadata_dir=False):

        json_data = self._load_metadata(json_file, use_app_metadata_dir)

        self.assertIsNotNone(json_data)

    def _test_enum_collisions(self, json_files, use_app_metadata_dir=False):

        enums = []
        collision_count = 0

        for file in json_files:

            json_data = self._load_metadata(file, use_app_metadata_dir)
            file_enums = []

            if json_data is not None:
                if json_data.get('enums') is not None and json_data.get('enums').get('enum') is not None:
                    file_enums = json_data['enums']['enum']
                else:
                    file_enums = None

            if file_enums:
                enums.extend(file_enums)

        if enums:

            value_dict = {}
            value_dict_rev = {}

            for enum in enums:

                enum_id = enum['id']
                enum_values = enum['values']
                for enum_item in enum_values:
                    key = enum_item['key']
                    value = enum_item['value']

                    if value_dict_rev.get(enum_id + "." + value):
                        collision_count = collision_count + 1
                        print("\nDuplicate VALUE '{}' found in ENUM '{}' "
                              "for KEY '{}' in JSON '{}'".format(value, enum_id, key, json_files))

                    if value_dict.get(enum_id + "." + key):
                        collision_count = collision_count + 1
                        print("\nDuplicate KEY '{}' found in ENUM '{}' "
                              "for VALUE '{}' in JSON '{}'".format(key, enum_id, value, json_files))

                    value_dict[enum_id + "." + key] = value
                    value_dict_rev[enum_id + "." + value] = key

        # make sure there are no collisions
        self.assertEqual(collision_count,0)

    def setUp(self):

        import sys, configparser

        from phenome import initialize_database

        self.absolute_path_of_test_directory = os.path.dirname(os.path.realpath(__file__))
        self.metadirectory = self.absolute_path_of_test_directory + "/../phenome/config/meta/"

        if len(sys._unit_tests_app_name) > 0:
            self.app_metadata_directory = self.absolute_path_of_test_directory + \
                                          "/../" + sys._unit_tests_app_name + "/config/meta/"
        else:
            self.app_metadata_directory = None

        # Monkey Patch the Dependency processor to allow for Object Model inheritance
        DependencyProcessor._verify_canload = CreateDB._verify_canload

        meta = CreateDB()

        if sys._unit_tests_loaded_system_data == False:
            meta.create()
            # create loads the system data and any unit test data as well
            sys._unit_tests_loaded_system_data = True
            sys._unit_tests_loaded_unit_test_data = True

        # load any APP specific META-DATA and CONFIG
        if sys._unit_tests_loaded_app_meta_data is False and self.app_metadata_directory is not None:

            # first load META
            meta = CreateDB()
            meta.load_specific_metadata_file(sys._unit_tests_app_name + ".json", self.app_metadata_directory)

            # Now load CONFIG
            settings = configparser.ConfigParser()
            settings.read(sys._unit_tests_app_name + ".ini")

            # set the flag, so we don't do it again during this APP test
            sys._unit_tests_loaded_app_meta_data = True

    def startSimulator(self, datafile, server_type, port):

        from phenome.tools.api_simulator import APISimulator

        args = ['-port', str(port), '-file', datafile, '-type', server_type]

        # create the simulator
        simulator = APISimulator()
        # pass the arguments
        simulator.setup(args)
        # start the thread
        simulator.daemon = True
        simulator.start()

        # give it a couple seconds to start up
        time.sleep(2)

        return simulator

    def get_first_model_id_from_classtype(self, model_classtype):

        from phenome_core.core.database.model.api import get_objectmodels_by_classtype

        models = get_objectmodels_by_classtype(model_classtype)
        for model in models:
            model_id = model.id
            break

        return model_id

    def _clean_db_objects_FULL(self):

        from phenome_core.core.database.model.api import get_object_by_ip, get_object_by_mac
        from phenome_core.core.database.model.object_model import ObjectModel

        try:
            # get our objects from test 4 and 5
            obj_ip = get_object_by_ip(CONST_TEST_IPADDRESS)
            if obj_ip:
                obj_ip.remove_relations()
                # when operating directly on the object, must commit immediately
                db_session.commit()

        except Exception as ex:
            print(ex)

        try:
            obj_mac = get_object_by_mac(CONST_TEST_MACADDRESS)
            if obj_mac:
                obj_mac.remove_relations()
                # when operating directly on the object, must commit immediately
                db_session.commit()
        except:
            pass

        try:
            obj_model_test = ObjectModel.query.filter_by(model=CONST_TEST_MODEL_TAG).first()

            if obj_model_test:
                obj_model_id = obj_model_test.id

                sql = "delete from property where (object_model_id = " + str(obj_model_id) + ")"
                db_session.execute(sql)

                sql = "delete from property_model where (object_model_id = " + str(obj_model_id) + ")"
                db_session.execute(sql)

                db_session.commit()

        except:
            pass

        # delete the RELATIONSHIPS of the objects we will create
        self._clean_db_relations()

        # delete the objects we will create (just in case) - but do not delete the "SELF" object

        sql = "delete from object where " \
              "(ip = '" + CONST_TEST_IPADDRESS + "' " \
                "or mac = '" + CONST_TEST_MACADDRESS + "' " \
                "or unique_id = '" + CONST_TEST_IPADDRESS + "' " \
                "or unique_id = '" + CONST_TEST_MACADDRESS + "')" \
                " and unique_id <> 'SELF'"

        db_session.execute(sql)
        db_session.commit()

        sql = "delete from object where " \
              "(ip = '" + CONST_TEST_IPADDRESS_2 + "' " \
                "or mac = '" + CONST_TEST_MACADDRESS_2 + "' " \
                "or unique_id = '" + CONST_TEST_IPADDRESS_2 + "' " \
                "or unique_id = '" + CONST_TEST_MACADDRESS_2 + "')" \
                " and unique_id <> 'SELF'"

        db_session.execute(sql)
        db_session.commit()

    def _clean_db_relations(self):

        CreateDB()._purge_relations()

        sql = "delete from relation where details like '%UNIT_TEST%'"
        db_session.execute(sql)
        db_session.commit()

    def _clean_db_model_helper_objects(self):

        from phenome_core.core.database.model.api import get_object_by_ip, get_object_by_mac

        # get our objects from all helper tests
        obj_ip = get_object_by_ip(CONST_TEST_IPADDRESS_ADD_DELETE_ONLY)
        if obj_ip:
            obj_ip.remove_relations()
            db_session.commit()

        obj_mac = get_object_by_mac(CONST_TEST_MACADDRESS_ADD_DELETE_ONLY)
        if obj_mac:
            obj_mac.remove_relations()
            db_session.commit()

        # delete the objects we will create (just in case) - but do not delete the "SELF" object
        sql = "delete from object where " \
              "(ip = '" + CONST_TEST_IPADDRESS_ADD_DELETE_ONLY + "' " \
                "or mac = '" + CONST_TEST_MACADDRESS_ADD_DELETE_ONLY + "' " \
                "or unique_id = '" + CONST_TEST_IPADDRESS_ADD_DELETE_ONLY + "' " \
                "or unique_id = '" + CONST_TEST_MACADDRESS_ADD_DELETE_ONLY + "')" \
                " and unique_id <> 'SELF'"

        db_session.execute(sql)
        db_session.commit()

    def _create_pdu_test_object(self, model_name):

        # Create a TEST PDU. But first DELETE, then ADD

        from phenome_core.core.database.model.api import get_objectmodel_by_name, \
            delete_object_by_ip_and_mac, refresh_object
        from phenome_core.core.helpers.model_helpers import add_object
        from test.supporting.test_results import BaseResultsTest
        results = BaseResultsTest()

        # delete if exists
        deleted = delete_object_by_ip_and_mac(self.CONST_TEST_PDU_IP, self.CONST_TEST_PDU_MAC, True, True)

        # get the model
        root_pdu = get_objectmodel_by_name(model_name)

        # create it
        pdu = add_object(root_pdu.model_classtype, root_pdu.id, self.CONST_TEST_PDU_IP,
                         self.CONST_TEST_PDU_MAC, 'ROOT_PDU_UNIT_TESTS')

        pdu.outlets = "1,2,3,4"
        pdu.username = 'admin'
        pdu.password = 'test'

        pdu = refresh_object(pdu)

        self.assertTrue(pdu.outlets=="1,2,3,4")

        # set the results object
        pdu.results = results

        return pdu

    def _create_sensor_test_object(self, model_name = 'TEST_SENSOR'):

        # Create a root Sensor. But first DELETE, then ADD

        from phenome_core.core.database.model.api import \
            get_objectmodel_by_name, delete_object_by_ip_and_mac, refresh_object
        from phenome_core.core.helpers.model_helpers import add_object
        from test.supporting.test_results import BaseResultsTest
        results = BaseResultsTest()

        # delete if exists
        deleted = delete_object_by_ip_and_mac(self.CONST_TEST_SENSOR_IP, self.CONST_TEST_SENSOR_MAC, True, True)

        # get the model
        root_sensor = get_objectmodel_by_name(model_name)

        # create it
        sensor = add_object(root_sensor.model_classtype, root_sensor.id,
                            self.CONST_TEST_SENSOR_IP, self.CONST_TEST_SENSOR_MAC,
                            'TEST_SENSOR_UNIT_TESTS')

        # There should be at least 1 action, powercycle
        self.assertTrue(len(sensor.actions) >= 1)

        # set a connected outlet
        sensor.connected_outlet = "1"

        # refresh, it should have the poweron action now
        sensor = refresh_object(sensor)
        self.assertTrue(sensor.actions.get('power_on')!=None)

        # set the results object
        sensor.results = results

        return sensor