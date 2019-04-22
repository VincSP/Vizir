import logging
import pprint

from dash.exceptions import PreventUpdate
from pandas import DataFrame

import data
from data import MongoManager

logger = logging.getLogger('dashvision.{}'.format(__name__))

class AppLogic():

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def experiment_options(self, db_name):
        exp_names = self.data_manager.get_experiment_names(db_name)
        exps_selector_options = ([{'label': name, 'value': name} for name in exp_names])
        return exps_selector_options


    def database_options(self, ):
        database_name = self.data_manager.get_database_names()
        database_options = []
        for db_name in database_name:
            database_options += [{'label': db_name, 'value': db_name}]
        return database_options

    def table_content_from_exp_names(self, db_name, exp_names, columns):
        cursor = self.data_manager.get_rows_from_exp_names(db_name, exp_names, columns)
        table_content = self.generate_experiment_table_rows(cursor, columns)
        return table_content


    def table_content_from_ids(self, db_name, selected_ids, columns):
        cursor = self.data_manager.get_rows_from_ids(db_name, selected_ids, columns)
        table = self.generate_experiment_table_rows(cursor, columns)
        return table


    def configs_from_ids(self, db_name, selected_ids):
        cursor = self.data_manager.get_configs_from_ids(db_name, selected_ids)
        res = []
        for elt in cursor:
            res.append(pprint.pformat(elt['config'], indent=4))

        return res


    def get_nested(self, d, keys):
        """
        get_nested(d, keys) create a list of key : value
        :param d: dict containing the wanted value
        :param keys: list of nested keys to get
        :return: the value corresponding to the nested keys
        """

        for k in keys:
            d = d[k]

        return d

    def generate_experiment_table_rows(self, cursor, columns):
        warn_missing = set()

        rows = []
        for exp in cursor:
            row = {}
            for col in columns:
                try:
                    row[col] = self.get_nested(exp, col.split('.'))
                except KeyError:
                    if col not in warn_missing:
                        warn_missing.add(col)
                        logger.warning('Requesting missing value: {}'.format(col))
                    row[col] = None
            rows.append(row)
        return rows

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

    def metric_names_from_ids(self, db_name, selected_ids):
        cursor = self.data_manager.get_metrics_infos(db_name, selected_ids)
        names = set()
        for elt in cursor:
            if 'metrics' in elt['info']:
                names.update([m['name'] for m in elt['info']['metrics']])
        return list(names)

    def metric_data_from_ids(self, metric_name, db_name, selected_ids):
        cursor = self.data_manager.get_metric_data(metric_name, db_name, selected_ids)
        return cursor