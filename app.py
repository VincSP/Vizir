import logging

import dash

from data import MongoManager
from logic import AppLogic

logger = logging.getLogger('dashvision.{}'.format(__name__))


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

data_manager = MongoManager(server='drunk', port='27017')
logic_manager = AppLogic(data_manager)
default_columns = ['_id', 'status']
