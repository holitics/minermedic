# test_mockobject.py (Unit Tests), Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from test.supporting.test_mockmodel import MockModel


class MockObject:

    def __init__(self):

        self.id = 1
        self.ip = '127.0.0.1'
        self.mac = 'ff:ff:ff:ff:ff:ff'
        self.unique_id = 'test_object'
        self.name = 'test_object'
        self.model = MockModel()
        self.model_id = self.model.id
        self.admin_disabled = False

    def __call_dynamic_action__(self, action_id):

        from phenome_core.core.handlers.action_handler import execute_dynamic_action
        return execute_dynamic_action(self, action_id)

    def get_power_usage_watts(self):

        from phenome.extensions.classtypes.OBJECT.powered_object import PoweredObject
        return PoweredObject.get_power_usage_watts(self)


class MockCoreAgent:

    def __init__(self):

        from phenome_core.core.constants import _CORE_AGENT_MODEL_CLASSNAME_
        from phenome_core.core.database.model.api import get_objectmodel_by_name, get_object_by_ip_and_model_id
        core_agent_model = get_objectmodel_by_name(_CORE_AGENT_MODEL_CLASSNAME_)

        # use the ID of the existing Core Agent, if this is testing on a machine with existing DB
        obj = get_object_by_ip_and_model_id("0.0.0.0", core_agent_model.id)

        if obj is not None:
            self.id = obj.id
        else:
            self.id = 1

        self.ip = '0.0.0.0'
        self.mac = 'aa:aa:aa:aa:aa:aa'
        self.unique_id = 'SELF'
        self.name = 'SELF'
        self.model = core_agent_model
        self.model_id = self.model.id
        self.admin_disabled = False
