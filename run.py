# run.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import threading, sys, subprocess


def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

# The first thing we need to do is to install the required Phenome Core
# if it is not currently installed in the environment

try:
    import phenome_core
except ImportError as ie:
    install('phenome-core')

# Now, supposedly the Phenome Core environment is setup.

# Create the flask application and load some libs
from phenome import flask_app
from phenome_core.core.base import basethread
from jinja2 import ChoiceLoader, FileSystemLoader


# defining function to run on shutdown
def close_running_threads():

    running_threads = threading.enumerate()
    base_thread = basethread.BaseThread

    for thread in running_threads:
        if isinstance(thread, base_thread):
            thread.stop()


def modify_template_loader():

    # create a loader for the default templates
    loader1 = FileSystemLoader("./phenome/static/lib/templates")
    # use the current default "loader" for the other loader
    loader2 = flask_app.jinja_loader
    # set the new ChoiceLoader into the loader
    flask_app.jinja_loader = ChoiceLoader([loader1, loader2])


if __name__ == '__main__':

    # install the cache so we do not hit APIs too many times
    # NOTE - Disabled due to breaking other functionality (like DLIPower devices). See Issue #105.
    # requests_cache.install_cache(cache_name='./phenome/data/api_cache', backend='sqlite', expire_after=55)

    from phenome import initialize_environment

    print("Starting MinerMedic...")

    # init the environment
    initialize_environment()

    # set the web listener port
    web_listen_port = flask_app.config['WEB_PORT'] # global_settings.get('WEB', 'Port')

    # first modify the loader so it can load up templates from default locations plus all blueprint locations
    modify_template_loader()

    # NOTE: When using debug, the use_reloader=False switch is needed. Might as well force to NOT reload by default.
    # see: https://stackoverflow.com/questions/9449101/how-to-stop-flask-from-initialising-twice-in-debug-mode

    is_debug = False

    if "--debug" in sys.argv:
        # just assume it's DEBUG mode..
        is_debug = True

    # Run the app and WAIT until finished
    flask_app.run(threaded=True, debug=is_debug, host='0.0.0.0', port=web_listen_port, use_reloader=False)

    # phenome is now closing...
    close_running_threads()

    print("MinerMedic has shutdown.")
