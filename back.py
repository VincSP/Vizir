import logging

import pymongo

logger = logging.getLogger('dashvision.{}'.format(__name__))


client = pymongo.MongoClient('drunk:27017')


def get_database_names():
    '''Populate dropdown with database on MongoDB/'''
    dbl = client.list_database_names()
    return dbl


def init_connection_to_runs(db_name):
    '''Generic function to access directly to runs collection of selected database'''
    db = client[db_name]
    return db['runs']


def get_experiment_names(db_name):
    ''''
    Returns a list of experiments of selected data_base

    :param db_name:
    :return:
    '''
    if db_name is None:
        return []
    collection = init_connection_to_runs(db_name)
    exp_names = collection.find({}, {'experiment.name': 1}).distinct('experiment.name')
    return exp_names


def on_load_database_options():
    database_options = []
    for db_name in get_database_names():
        database_options += [{'label': db_name, 'value': db_name}]
    return database_options


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


def get_table_content(db_name, exp_names, columns):
    collection = init_connection_to_runs(db_name)

    filter = {'experiment.name': {'$in': exp_names}}
    projection = dict((col, True) for col in columns)

    cursor = collection.find(filter=filter, projection=projection)

    return generate_experiment_table_rows(cursor, columns)
