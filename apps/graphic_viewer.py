import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go


from dash.dependencies import Input, Output, State

from app import app, default_columns, logic_manager

layout = html.Div([
    html.H3('Graph'),
    html.Div(id='tab-data', style={'display': 'none'}),
    html.Div(
        dcc.Graph(id='graph')
    )

])