import pymongo

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