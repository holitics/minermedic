# minermedic_tools_001_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import os, sys, pytest, unittest, logging, configparser
from test import BaseTest

CONST_APP_NAME = 'minermedic'

CONST_API_PORT = 6001

class TestMinerDumper(BaseTest):

    def setUp(self):

        global CONST_API_PORT
        # increment the port
        CONST_API_PORT = CONST_API_PORT + 1

        # set the port
        self.api_port = CONST_API_PORT

        sys._unit_tests_load_app_meta_data = True
        super(TestMinerDumper, self).setUp()
        settings = configparser.ConfigParser()
        settings.read(CONST_APP_NAME + ".ini")

    def test_dumper_parser_001_with_simulator(self):

        from phenome.tools.miner_dumper import MinerDumper

        # tell the REST API which URLS to simulate, which port to target
        sys._unit_tests_API_SIMULATE_URLS = None
        sys._unit_tests_API_TARGET_LOC = self.CONST_SIMULATOR_API_TARGET_LOC
        sys._unit_tests_API_TARGET_PORT = self.api_port

        # get path to data file
        simulator_data_path = self.absolute_path_of_test_directory + "/apps/minermedic/resources/miners/antminer_s9.py"

        # start the simulator
        simulator = self.startSimulator(simulator_data_path, 'JSON_RPC', self.api_port)

        try:

            # create the dumper
            dumper = MinerDumper()


            # TEST 1!!
            args = ['-ip', '0.0.0.0', '-port', str(self.api_port)]
            dumper.contact(args)
            output = dumper.get_last_response()
            # should get the POOLS
            self.assertEqual(output['POOLS'][0]['URL'],'stratum+tcp://sha256.usa.nicehash.com:3334')

            # another test, a specific call to 'stats', get the ID
            args = ['-ip', '0.0.0.0', '-port', str(self.api_port), '-cmd', 'stats']
            dumper.contact(args)
            output = dumper.get_last_response()
            self.assertEqual(output['STATS'][1]['ID'],'BC50')


        except Exception as ex:
            pass

        finally:

            try:
                simulator.stop()
            except:
                pass
