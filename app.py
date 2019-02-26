import logging

import dash

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


columns = ['_id', 'status']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
