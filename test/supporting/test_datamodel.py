# test_datamodel.py (Unit Tests), Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>


def get_test_results_with_datamodel(clear_old_datamodel):

    from phenome_core.core.globals import datamodel_maps
    from test.supporting.test_results import BaseResultsTest

    # define a datamodel
    datamodel = [
        {"name": "result_one", "description": "result # 1", "value_type": "TEXT",
         "default": "", "attributes": [{"value_type": "INTEGER", "units": "none", "aggr": "mean"}]},
        {"name": "result_two", "description": "result # 2", "value_type": "TEXT",
         "default": "", "attributes": [{"value_type": "INTEGER", "units": "none", "aggr": "sum"}]},
        {"name": "result_three", "description": "result # 3", "value_type": "TEXT",
         "default": "", "attributes": [{"value_type": "INTEGER", "units": "none", "aggr": "min"}]},
        {"name": "result_four", "description": "result # 4", "value_type": "TEXT",
         "default": "", "attributes": [{"value_type": "INTEGER", "units": "none", "aggr": "max"}]},
        {"name": "result_five", "description": "result # 5", "value_type": "TEXT",
         "default": "", "attributes": [{"value_type": "INTEGER", "units": "{ENUM._MODEL_CLASSTYPES_}", "aggr": "max"}]},
    ]

    dictmodel = {}
    for item in datamodel:
        dictmodel[item['name']] = item

    # set the datamodel in the maps
    datamodel_maps['TEST_RESULTS'] = dictmodel

    if clear_old_datamodel:
        from phenome_core.core.globals import stats_collector
        if stats_collector.get('TEST_RESULTS') is not None:
            stats_collector['TEST_RESULTS'] = None

    # create a resultsTest object
    results = BaseResultsTest()

    return results


def get_specific_model_results(data_model_name, clear):

    from phenome_core.core.base.base_results import BaseResults
    from phenome_core.core.globals import stats_collector

    if clear:
        if stats_collector.get(data_model_name) is not None:
            stats_collector[data_model_name] = None

    # create a results object based on the specified datamodel
    results = BaseResults(data_model_name)

    return results


def add_datarow_to_test_results(results, object, row_data):

    # clear from previous row
    results.clear_results()

    # set the result
    results.set_result(object,'result_one',row_data[0]) # use a float
    results.set_result(object,'result_two',row_data[1])
    results.set_result(object,'result_three',row_data[2])
    results.set_result(object,'result_four',row_data[3])
    if len(row_data)==5:
        results.set_result(object,'result_five',row_data[4])

    # update the datamodel with the first set of data
    results.update_datamodel()


def add_datarow_to_results(results, object, row_kpis, row_data):

    # clear from previous row
    results.clear_results()

    # set the result
    for x in range(len(row_data)):
        results.set_result(object,row_kpis[x],row_data[x])

    # update the datamodel with the first set of data
    results.update_datamodel()


def build_datamodel_test_results(model, kpis, row_data, object, row_count, clear):

    # create a results object
    results = get_specific_model_results(model, clear)

    row = []
    # add the rows
    for x in range(row_count):
        row = row_data
        for y in range(len(row_data)):
            row[y] = row_data[y] + x

        add_datarow_to_results(results, object, kpis, row)


