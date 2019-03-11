import logging
from pandas import DataFrame
import pymongo
from dash.exceptions import PreventUpdate


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

    def filter_rows_by_query(self, rows, query):
        '''
        Returns rows that are filtered by the query.
        Uses the pandas.DataFrame.query method
        '''

        if query.strip() == '':
            return rows

        df = DataFrame(rows)

        # temporarily replacing '.' in columns to '__'
        # for pandas syntax reasons
        normalize_col_names = lambda x: x.replace('.', '___')
        before_columns = df.columns
        df_renamed = df.rename(columns=normalize_col_names)

        # filter rows with query
        try:
            df_filtered = df_renamed.query(normalize_col_names(query), local_dict={})
        except Exception as e:
            logger.warning(f'Error in query "{query}": {e}')
            raise PreventUpdate
        
        # recovering origin column names
        denormalize_col_names = lambda x: x.replace('___', '.')
        df_filtered = df_filtered.rename(columns=denormalize_col_names)

        # check column integrity
        if (df_filtered.columns != df.columns).any():
            col_diff = [f'{c} -> {cf}' for c, cf in zip(df.columns, df_filtered.columns) if c != cf]
            logger.warning(f'Columns {", ".join(col_diff)} differ before and after query.')
            raise PreventUpdate

        filtered_rows = df_filtered.to_dict('rows')
        return filtered_rows

