import logging

import pymongo

logger = logging.getLogger('dashvision.{}'.format(__name__))


def get_nested(d, keys):
    """
    get_nested(d, keys) create a list of key : value
    :param d: dict containing the wanted value
    :param keys: list of nested keys to get
    :return: the value corresponding to the nested keys
    """

    for k in keys:
        d = d[k]

    return d

def generate_experiment_table_rows(cursor, columns):
    warn_missing = set()

    rows = []
    for exp in cursor:
        row = {}
        for col in columns:
            try:
                row[col] = get_nested(exp, col.split('.'))
            except KeyError:
                if col not in warn_missing:
                    warn_missing.add(col)
                    logger.warning('Requesting missing value: {}'.format(col))
                row[col] = None
        rows.append(row)
    return rows


class MongoManager():
    def __init__(self, server='localhost', port='27017'):
        self._client = pymongo.MongoClient('{}:{}'.format(server, port))

    def _get_database_names(self,):
        '''Populate dropdown with database on MongoDB/'''
        dbl = self._client.list_database_names()
        return dbl

    def _init_connection_to_runs(self,db_name):
        '''Generic function to access directly to runs collection of selected database'''
        db = self._client[db_name]
        return db['runs']

    def on_load_database_options(self):
        database_options = []
        for db_name in self._get_database_names():
            database_options += [{'label': db_name, 'value': db_name}]
        return database_options

    def get_experiment_names(self, db_name):
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

    def get_table_content(self, db_name, exp_names, columns):
        collection = self._init_connection_to_runs(db_name)

        filter = {'experiment.name': {'$in': exp_names}}
        projection = dict((col, True) for col in columns)

        cursor = collection.find(filter=filter, projection=projection)

        return generate_experiment_table_rows(cursor, columns)
