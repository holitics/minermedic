# test_pdu.py (Unit Tests), Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome.extensions.classtypes.POWER_DISTRIBUTION_UNIT.base_pdu import BasePDU


class TestPDU(BasePDU):

    __test__ = False

    def __init__(self):
        super(TestPDU, self).__init__()

    def test_multiple_arguments(self, arg1, arg2, arg3):
        # called through the action handler
        print(arg1, arg2, arg3)
        return True

    def test_cps(self, arg1):
        self.power_state = arg1
        return True
