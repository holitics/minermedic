# Copyright (c) 2018, Anastasios Selalmazidis: Initial Implementation
# Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Updated implementation, added more miners


from phenome.extensions.lib.pycgminer import CgminerAPI
from phenome import flask_app

"""

CGMiner API. 

Offers specific vendor based commands through the standard CGMiner RPC API.
Each vendor can be set to have a different set of ports, although it is usually always the same port (4028)

"""


def get_type(ip, port):

    """
    Attempts to try to get the type of miner from the stats command

    Returns:
        String - if miner type is found
        None - if command failed

    """

    cgminer = CgminerAPI(host=ip, port=port, payload_command="command")
    output = cgminer.stats()
    miner_type = None
    try:
        miner_type = output['STATS'][0]['Type']
    except:
        pass

    if miner_type is None:
        pass
    else:
        pass

    return miner_type


def get_summary(ip):

    """
    Get the output from miner "summary()" command.

    Returns:
        dict
    """

    # works with most CGMiner Miners
    cgminer = CgminerAPI(host=ip)
    output = cgminer.summary()
    output.update({"IP": ip})
    return dict(output)


def get_pools(ip):

    """
    Get the output from miner "pools()" command.
    Works with most CGMiner miners.

    Returns:
        dict
    """

    cgminer = CgminerAPI(host=ip)
    output = cgminer.pools()
    output.update({"IP": ip})
    return dict(output)


def get_baikal_devs(ip):

    """
    Get the board statistics for a Baikal Miner.

    Returns:
        dict
    """

    port = flask_app.config.get("MINER_API_PORTS_BAIKAL_PORT");
    cgminer = CgminerAPI(host=ip,port=port,payload_command="command")
    output = cgminer.devs()
    output.update({"IP": ip})
    return dict(output)


def get_claymore_stats(ip):

    """
    Get the statistics for a Claymore Miner

    Returns:
        dict
    """

    port = flask_app.config.get("MINER_API_PORTS_CLAYMORE_PORT");
    cgminer = CgminerAPI(host=ip,port=port,payload_command="method")
    output = cgminer.miner_getstat1()
    output.update({"IP": ip})
    return dict(output)


def get_claymore_configfile(ip, filename):

    """
    Get the configuration file for a Claymore Miner

    Returns:
        dict
    """

    port = flask_app.config.get("MINER_API_PORTS_CLAYMORE_PORT");
    cgminer = CgminerAPI(host=ip,port=port,payload_command="method",parameter_argument="params",encapsulate_args=True)
    output = cgminer.miner_getfile(filename)
    output.update({"IP": ip})
    return dict(output)


def reboot_claymore_miner(ip):

    """
    Sends a command to reboot a Claymore Miner

    Returns:
        dict - containing success or failure
    """

    port = flask_app.config.get("MINER_API_PORTS_CLAYMORE_PORT");
    cgminer = CgminerAPI(host=ip,port=port,payload_command="method")
    output = cgminer.miner_reboot()
    output.update({"IP": ip})
    return dict(output)


def restart_claymore_miner(ip):

    """
    Sends a command to restart a Claymore Miner

    Returns:
        dict - containing success or failure
    """

    port = flask_app.config.get("MINER_API_PORTS_CLAYMORE_PORT");
    cgminer = CgminerAPI(host=ip,port=port,payload_command="method")
    output = cgminer.miner_restart()
    output.update({"IP": ip})
    return dict(output)


def get_cgminer_stats(ip):

    """
    Retrieves statistics from a Miner using generic CGMiner API and Port

    Returns:
        dict
    """

    port = flask_app.config.get("MINER_API_PORTS_CGMINER_PORT");
    cgminer = CgminerAPI(host=ip, port=port,payload_command="command")
    output = cgminer.stats()
    output.update({"IP": ip})
    return dict(output)


def get_cgminer_devs(ip):

    """
    Retrieves boards statistics for Miners using generic CGMiner API and Port

    Returns:
        dict
    """

    port = flask_app.config.get("MINER_API_PORTS_CGMINER_PORT");
    cgminer = CgminerAPI(host=ip,port=port,payload_command="command")
    output = cgminer.devs()
    output.update({"IP": ip})
    return dict(output)

def get_antminer_stats(ip):

    """
    Retrieves statistics for an Antminer Miner

    Returns:
        dict
    """

    port = flask_app.config.get("MINER_API_PORTS_ANTMINER_PORT");
    cgminer = CgminerAPI(host=ip, port=port,payload_command="command")
    output = cgminer.stats()
    output.update({"IP": ip})
    return dict(output)


def get_avalon_stats(ip):

    """
    Retrieves statistics for an Avalon Controller

    Returns:
        dict
    """

    port = flask_app.config.get("MINER_API_PORTS_AVALON_PORT");
    cgminer = CgminerAPI(host=ip, port=port,payload_command="command")
    output = cgminer.stats()
    output.update({"IP": ip})
    return dict(output)


def get_avalon_devs(ip):

    """
    Retrieves statistics for Avalon Miners attached to the controller

    Returns:
        dict
    """

    port = flask_app.config.get("MINER_API_PORTS_AVALON_PORT");
    cgminer = CgminerAPI(host=ip,port=port,payload_command="command")
    output = cgminer.devs()
    output.update({"IP": ip})
    return dict(output)
