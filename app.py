import logging

import dash

logger = logging.getLogger('dashvision.{}'.format(__name__))


columns = ['_id', 'status']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
