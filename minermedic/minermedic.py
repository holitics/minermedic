# minermedic.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome_core.core.base.logger import root_logger as logger
from phenome_core.core import ui
from phenome_core.core.constants import  _API_ERROR_CODES_, _API_ERROR_MESSAGES_
from minermedic.constants import _MINERMEDIC_API_V1_PREFIX_

from phenome_core.core.database.model.api import get_object_by_ip, delete_object

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify
)

# define the blueprint for the minermedic phenome
minermedic = Blueprint('minermedic', __name__, template_folder='./templates')

"""

MinerMedic - Main Entrypoints for the MinerMedic Applicaton.

All the API entrypoints for the MinerMedic UI are defined in this Blueprint.

"""

@minermedic.route('/')
def miner_home():

    """
    Generates the Home Screen
    :return: HTML Template with the Home Screen
    """

    return ui.info()


@minermedic.route('/update_object_properties', methods=['POST'])
def update_object_properties():

    return ui.update_object_properties(request)


@minermedic.route('/object_dialog/<id>/<header_only>/<show_details>')
def object_dialog(id, header_only, show_details):

    """
    Generates an Object Dialog Template, usually shown as a PopUp
    :param id: Object ID
    :param header_only: Show the Top part of the Dialog Only (handled by template)
    :param show_details: Show the object details (handled by template)
    :return: HTML Template with the Object Dialog and contents
    """

    return ui.object_dialog(None, id, header_only, show_details)


@minermedic.route('/status')
def miner_status():

    """
    Generates a UI Status screen for MinerMedic App
    :return: HTML Template with Status information
    """
    return ui.status()


@minermedic.route('/messages')
def miner_messages():

    """
    Generates a set of "messages" for the MinerMedic App
    :return: HTML Template for Messages
    """
    return ui.messages()


@minermedic.route('/profitability')
def miner_profitability():

    """
    Returns the MinerMedic Profitability Screen
    :return: HTML Template for Profitability
    """

    logger.debug("/profitability - remote addr:" + request.remote_addr)
    # render the template
    return render_template('profitability.html', version='0.0')


@minermedic.route('/predictions')
def miner_predictions():

    """
    Returns a Model Template Prediction Status screen
    :return: HTML Template for Model Prediction Status
    """

    logger.debug("/predictions - remote addr:" + request.remote_addr)
    # render the template
    return render_template('predictions.html', version='0.0')


@minermedic.route('/hashrate')
def miner_hashrate():

    """
    Generates the MinerMedic HashRate Screen
    :return: HTML Template with Hashrate Information
    """

    logger.debug("hashrate() - remote addr:" + request.remote_addr)
    return render_template('hashrate.html', version='0.0')


@minermedic.route('/hashrate_by_model')
def hashrate_by_model():

    """
    Creates a JSON dict of HashRates By Model. Can be called directly.
    Used by an AJAX js method called by "/hashrate" screen.

    :return: JSON with Hashrate Info
    """

    from phenome_core.core.globals import results_collector
    model_hashrates = dict()

    try:
        model_hashrates = results_collector['CRYPTO_MINER'].hash_rate_per_model
    except:
        pass

    model_list = []
    x = 0

    for model,value in model_hashrates.items():
        text = "{} - {:3.2f} {} ".format(model, value["sum_current"], value["units"])
        sum_hashrate = value["sum_current"]
        max_hashrate = value["sum_max"]
        if sum_hashrate < 0:
            sum_hashrate = 0
        if max_hashrate <= 0:
            max_hashrate = 1
        score = sum_hashrate/max_hashrate * 100
        x = x + 1
        if score>0:
            score = "{:3.2f}".format(score)
            model_list.append({"id": model, "order": x, "score": score, "weight": score, "label": text})

    return jsonify(model_list)


def __add_miner(ip_address, model_id):

    """
    Internal method to add a miner.
    :param ip_address: IP Address of the Miner
    :param model_id: Model ID of the Miner
    :return: Boolean
    """

    from phenome_core.core.helpers.model_helpers import add_object
    obj = add_object('CRYPTO_MINER', model_id, ip_address, None, None)
    return obj is not None


@minermedic.route(_MINERMEDIC_API_V1_PREFIX_ + '/add_miner/<ip_address>/<model_id>')
def api_add_miner(ip_address, model_id):

    """
    Adds a Miner Object via the REST API
    e.g.:  http://localhost:5000/minermedic/api/v1/add_miner/192.168.1.223/17

    Please Note - when adding a Miner from the UI, this endpoint is NOT CALLED.
    Instead, the __add_object_internal API call is called in the core REST API.
    This endpoint is a convenience method for other 3rd party implementations.

    :param ip_address: The IP address of the Miner to add
    :param model_id: The Model ID of the Miner to add
    :return: JSON response including new Miner ID if successful
    """

    from flask.json import jsonify

    success = __add_miner(ip_address, model_id)

    if success:
        status = _API_ERROR_CODES_['OK'].value
        error = _API_ERROR_MESSAGES_['OK'].value
        miner_id = get_object_by_ip(ip_address).id
    else:
        status = _API_ERROR_CODES_['OP_FAILED'].value
        error = _API_ERROR_MESSAGES_['OP_FAILED'].value
        miner_id = -1

    response = {"status": status,
                "error": error,
                "id": miner_id}

    return jsonify(data=[response])


@minermedic.route(_MINERMEDIC_API_V1_PREFIX_ + '/delete/<id>')
def delete_miner(id):

    """
    Deletes a Miner using a Rest API call
    :param id: Miner ID for Miner to delete
    :return: JSON with status
    """

    # delete the miner object from the system
    success = delete_object(id, False, True)

    response = {"status": success,
                "id": id}

    return response
