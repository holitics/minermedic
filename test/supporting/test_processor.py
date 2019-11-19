# test_processor.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome_core.core.base.base_processor import BaseProcessor


class TestProcessor(BaseProcessor):

    __test__ = False

    def __init__(self):
        super(TestProcessor, self).__init__()

    def process(self, results):

        from test.supporting.test_mockobject import MockObject

        test_value = 45

        object = MockObject()
        object.id = 1

        # here we would normally POLL the object

        # populate the value with 45
        results.set_result(object, 'test_value', test_value)

        return results

