import logging

import dash
from flask_caching import Cache
from back import MongoManager

logger = logging.getLogger('dashvision.{}'.format(__name__))


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT = 60

data_manager = MongoManager(server='drunk', port='27017')
default_columns = ['_id', 'status']
