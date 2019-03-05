import logging

import dash

from back import MongoManager

logger = logging.getLogger('dashvision.{}'.format(__name__))


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

data_manager = MongoManager(server='127.0.0.1', port='27018')
default_columns = ['_id', 'status']
