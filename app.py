import logging

import dash

from back import MongoManager

logger = logging.getLogger('dashvision.{}'.format(__name__))


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data_manager = MongoManager(server='localhost', port='27017')
default_columns = ['_id', 'status']
