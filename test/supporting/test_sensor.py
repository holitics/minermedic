
from phenome.extensions.classtypes.ENVIRONMENT_SENSOR.base_sensor import BaseSensor

class TestSensor(BaseSensor):

    __test__ = False

    def __init__(self):
        super(TestSensor, self).__init__()


    def test_multiple_arguments(self, arg1, arg2, arg3):
        # called through the action handler
        print(arg1, arg2, arg3)
        return True




