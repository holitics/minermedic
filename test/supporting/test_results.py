# test_results.py (Unit Tests), Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome_core.core.base.base_results import BaseResults


class BaseResultsTest(BaseResults):

    __test__ = False

    def __init__(self):

        super(BaseResultsTest, self).__init__('TEST_RESULTS')
        self.set_notify_enabled(False)

