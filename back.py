import pymongo
client = pymongo.MongoClient('drunk:27017')

# Populate dropdown with database on MongoDB/


def get_database_name():
    dbl = client.list_database_names()
    return dbl

# Generic function to access directly to runs collection of selected database


def init_connection_to_runs(selected_database):
    db = client[selected_database]
    return db['runs']

def get_experience(selected_database):
    """
    Returns a list of experiences of selected data_base

    :param selected_database:
    :return:
    """
    if selected_database is None:
        return []
    collection = init_connection_to_runs(selected_database)
    list = []
    for x in collection.find({}, {'experiment.name': 1}).distinct('experiment.name'):
        list.append(x)
    return list

def on_load_database_options():
    database_options = (
        [{'label': database, 'value': database}
         for database in get_database_name()]
    )
    return database_options