# base_pool.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.database.model.object import Object
from minermedic.pools.helper import pool_objects
from phenome_core.core.helpers.model_helpers import get_relation_type_id, get_model_classtype_id_by_name, autogenesis
from phenome_core.util.filesystem import get_class_fully_qualified_path
from phenome_core.core.registered_apps import get_app_id
from phenome_core.core.base.logger import root_logger as logger

"""

BasePool

    This is the base definition of all CRYPTO_MINING_POOL objects.
    
    All Mining Pools should subclass this object in order to provide a 
    pool specific implementation of their APIs and data.

"""


class BasePool():

    CLASSTYPE = "CRYPTO_MINING_POOL"
    _MINER_URL = ""
    _pool_object = None
    _pool_params = None

    _DEFAULT_COIN_ = "BTC"

    def __init__(self, pool, pool_attrs):

        # Check to see if this object has yet been auto-created in the Phenome

        # set the pool object
        self._pool_object = pool_objects.get(pool)

        if self._pool_object is None:
            # we need to autogen
            self.__create(pool, pool_attrs)
        else:
            # TODO - we may need to reload the object just in case configuration has changed
            pass

    def build_creation_parameters(self, pool, pool_attrs, pool_classname):

        """
        Builds a set of parameters to be used by the system to create a Mining Pool Object

        Returns:
                dict
        """

        params = {}

        # FOR THE OBJECT MODEL
        params['app_id'] = get_app_id('minermedic')
        params['model_name'] = self.CLASSTYPE + "_" + pool_attrs['name'].upper()
        params['model_classtype'] = self.CLASSTYPE
        params['model_description'] = pool_attrs['description']
        params['model_classname'] = pool_classname

        # FOR THE OBJECT
        # name of the object that will be created
        params['ip_address'] = pool

        # Set the unique ID of the pool by using the POOL URL - this can be overridden in the subclasses
        params['unique_id'] = pool

        return params

    def __create(self, pool, pool_attrs):

        if self._pool_params is None:
            # build parameters needed to create a pool model, pool object
            params = self.build_creation_parameters(pool, pool_attrs, get_class_fully_qualified_path(self))

        # Perform autogenesis
        object = autogenesis(params)

        if object is not None:
            if isinstance(object, str):
                # check some error messages
                if object == "Object already exists" or object == "Could not create object":
                    # maybe we need to look up by IP or unique ID instead
                    pass
            elif (isinstance(object, Object)):
                pool_objects[pool] = object
                self._pool_object = object

    def relate(self, miner):

        """
        Creates a relationship between the Miner and the Mining Pool

        Returns:
                None
        """

        try:

            from phenome_core.core.database.db import db_session

            # by default we will not update db
            updated_db = False

            # find out if there is a relationship from this miner to this pool
            if miner.has_relation(self._pool_object) == False:

                # get the "MINING_ON" relationship
                rtype_id = get_relation_type_id('MINING_ON')

                # add the relation
                miner.add_relation(self._pool_object, rtype_id, None)

                # commit so the model will fill in the relation objects, etc.
                db_session.commit()

            # are there any relations of classtype MINING POOL
            relations = miner.get_relations_by_classtype(get_model_classtype_id_by_name(self.CLASSTYPE))

            if relations:

                # reset the flag
                updated_db = False

                # iterate through relations to pools, and disable all relations except for the one to the current pool
                for r in relations:
                    if r.object_to is not None and r.object_to.id == self._pool_object.id:
                        if r.enabled == False:
                            r.enabled = True
                            updated_db = True
                    elif r.enabled == True:
                        r.enabled = False
                        updated_db = True

                if updated_db:
                    db_session.commit()

        except:
            logger.error("ERROR creating relationship between miner '{}' to pool '{}'".format(miner.id, self._pool_object.unique_id))

    def parse_json(self, json, results, miner, worker, pool, algo, algo_idx, coin_idx, coin_cost):

        """
        Parses the JSON data retrieved from the Mining Pool's API.
        This method must be implemented per POOL and is a POOL
        dependent implementation of how to parse the data.

            The following stats are to be collected from the pool:

            - "profitability" - This is a measure of COIN / speed suffix / per DAY
                                This is a calculated stat, usually.
                                Sometimes several metrics are needed

                                e.g. profitability = ((coins_mined_per_minute * (60 * 24))/speed_accepted)

            - "speed_accepted" - The "accepted" hashrate by the pool (i.e. what miner gets paid on).
                                Almost all pools report on this

            - "speed_reported" - The "reported" hashrate by the pool (i.e. how much work the miner
                                reports to the pool that it is doing). If this is not available from
                                the pool or the miner is not sending it, set to NONE, do NOT set to 0.

            - "speed_suffix"   - The "units" that the pool is reporting hashrate in (e.g. 'MH')

            Sometimes not all these statistics can be retrieved, as some APIs are less verbose.
            In those cases the implementation will have to fill in the gaps.

            Once stats are collected, pass them to "create_api_results",
            then pass that dict to the "set_api_results",
            along with any other information passed in

        """

        pass

    def get_pool_stats(self, results, miner, worker, algo, pool_id, pool_url):

        """
        Pool specific implementation that calls to the Pool API and then passes the response to "parse_json"

        :param results: The MinerResults object
        :param miner: The Miner object
        :param worker: The worker (string)
        :param algo: The algo being mined (string)
        :param pool_id: The Pool ID (integer)
        :param pool_url: The original passed pool url

        :return: None

        """

        pass


