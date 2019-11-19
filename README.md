# MinerMedic

![Build status](https://api.travis-ci.com/holitics/minermedic.svg?token=sxJbjzY55bRNhaRxizPp&amp;branch=master)

MinerMedic is a CryptoCurrency Miner Monitoring, Automation, and Prediction tool based on the [Phenome AI](https://phenome.ai/) platform. Visit the [MinerMedic](https://phenome.ai/apps/minermedic/) page to learn more or to download a pre-built package that already includes the [Phenome Extensions](https://github.com/holitics/phenome-extensions).

MinerMedic is written completely in Python (supporting v3.6+) and so can run on a variety of platforms including OSX, Linux deviants, Windows, and hardware including small ARM based devices like Raspberry PI, Jetson Nano, etc. 

MinerMedic is a **Flask Application**. It has a REST API and a simple embedded UI interface. If you are familiar with Python, Flask and JSON, it's fairly easy to add new Miners, Pools, and features. Contributions to the project are highly welcome!

## Getting Started

Please note, these instructions assume you have a minimum of [Python 3.6](https://www.python.org/downloads/) and [git](https://git-scm.com/downloads) installed.

First clone the source:
```
$ git clone https://github.com/holitics/minermedic
```

then change into the directory:

```
$ cd minermedic
```

create a base INI file:
```
$ cp minermedic/minermedic.ini.dist ./minermedic.ini
```

If you would like, you should edit this file and put in your Mail Server information, etc. It is pretty self-explanatory. Detailed documentation on the INI file forthcoming.

## Install the dependencies

The Phenome core will be needed:
```
$ pip install phenome-core --extra-index-url https://api.packagr.app/AvVcpYfO2/
```
then clone the extensions directly into the minermedic source directory:
```
$ git clone https://github.com/holitics/phenome-extensions phenome
```

At this point minermedic should be runnable. Let's try it out!

## Run the app locally

```
$ ./run.sh
```
If you haven't followed the previous instructions it will try to install the dependencies. Once it is ready and has started, you should see some information print to the screen:
```
Starting MinerMedic...
Opening Database, please wait ...
Loading Object Model, please wait ...
Object Model loaded in 4117ms
Using TensorFlow backend.
 * Serving Flask app "phenome" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
WARNING: Logging before flag parsing goes to stderr.

Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)

```

Everything else will probably go to the log. There should be a "/log" directory created automatically.

## Check the UI in browser
[MinerMedic Local UI](http://localhost:8080/)

## Access the API
```
$ curl http://localhost:8080/api/v1/helloworld
```

## Run Unit Tests

```
$ ./run_tests.sh
```

## Development Environment

At this point you should be ready to start running / debugging the application in the IDE. If you have PyCharm, simply go to "File" -> "Open" and point to the **minermedic** folder. Once opened, create a Run/Debug configuration by going to "Run" -> "Edit Configurations".

![Debug Configuration For PyCharm](http://phenome.ai/wp-content/uploads/2019/11/PyCharm_DEBUG_Config.png)

Make sure to use **Python 3.6+**. Also for a DEBUG configuration, make sure to add the parameters: **"--debug True"**
