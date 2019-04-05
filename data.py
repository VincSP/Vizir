import pymongo


class MongoManager():
    def __init__(self, server='localhost', port='27017'):
        self._client = pymongo.MongoClient(server, int(port))

    def _get_database_names(self, ):
        '''Populate dropdown with database on MongoDB/'''
        dbl = self._client.list_database_names()
        return dbl

    def _init_connection_to_runs(self, db_name):
        '''Generic function to access directly to runs collection of selected database'''
        db = self._client[db_name]
        return db['runs']

    def _on_load_database_options(self):
         db_name = self._get_database_names()
         return db_name

    def _get_experiment_names(self, db_name):
        ''''
        Returns a list of experiments of selected data_base

        :param db_name:
        :return:
        '''
        if db_name is None:
            return []
        collection = self._init_connection_to_runs(db_name)
        exp_names = collection.find({}, {'experiment.name': 1}).distinct('experiment.name')
        return exp_names

    def _get_table_content_from_exp_names(self, db_name, exp_names, columns):
        collection = self._init_connection_to_runs(db_name)

        filter = {'experiment.name': {'$in': exp_names}}
        projection = dict((col, True) for col in columns)

        cursor = collection.find(filter=filter, projection=projection)

        return cursor

    def _get_table_content_from_ids(self, db_name, selected_ids, columns):
        collection = self._init_connection_to_runs(db_name)

        filter = {'_id': {'$in': selected_ids}, }
        projection = dict((col, True) for col in columns)

        cursor = collection.find(filter=filter, projection=projection)

        return cursor

    def _get_configs_from_ids(self, db_name, selected_ids):
        collection = self._init_connection_to_runs(db_name)
        filter = {'_id': {'$in': selected_ids}, }
        projection = dict(config=True)
        cursor = collection.find(filter=filter, projection=projection)

        return cursor

