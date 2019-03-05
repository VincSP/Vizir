import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app, data_manager

layout = html.Div([
    html.H3('Configs'),
    html.Div(id='tab-data', style={'display': 'none'}),

    html.Div([
        html.Div(dcc.Dropdown(id='run-selector-1')),
        html.Pre(id='preformated-data-1'), ],
        className='five columns'),
    html.Div([
        html.Div(dcc.Dropdown(id='run-selector-2')),
        html.Pre(id='preformated-data-2')],
        className='five columns')
])


for i in [1, 2]:
    @app.callback(Output('run-selector-{}'.format(i), 'options'),
                  [Input('tab-data', 'data')],
                  [State('run-selector-{}'.format(i), 'value')])
    def populate_configs(data_args, previous_value):
        if data_args is None:
            return 'No data'
        return ([{'label': 'Experience {}'.format(id), 'value': id} for id in data_args['selected_ids']])

    @app.callback(Output('preformated-data-{}'.format(i), 'children'),
                  [Input('run-selector-{}'.format(i), 'value')],
                  [State('tab-data', 'data'),
                   State('preformated-data-{}'.format(i), 'children')])
    def populate_configs(selected_run, data_args, previous_entry):
        if data_args is None:
            return 'No data'
        return data_manager.get_configs_from_ids(data_args['db'], [selected_run])
