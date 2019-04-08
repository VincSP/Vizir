import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app, logic_manager

layout = html.Div([
    html.H3('Configs'),
    html.Div(id='tab-data', style={'display': 'none'}),

    html.Div([
        html.Div([
            html.Div(dcc.Dropdown(id='run-selector-0')),
            html.Pre(id='preformated-data-0'), ],
            className='six columns'),
        html.Div([
            html.Div(dcc.Dropdown(id='run-selector-1')),
            html.Pre(id='preformated-data-1')],
            className='six columns')],
        className='row')])


for i in [0, 1]:
    @app.callback(Output('run-selector-{}'.format(i), 'options'),
                  [Input('tab-data', 'data')])
    def populate_dropdown(data_args):
        if data_args is None:
            return []

        selected_ids = data_args.get('selected_ids', [])
        return [{'label': 'Experience {}'.format(id), 'value': id} for id in selected_ids]

    @app.callback(Output('run-selector-{}'.format(i), 'value'),
                  [Input('run-selector-{}'.format(i), 'options')])
    def dropdown_default(options, idx=i):
        if len(options) > 1:
            return options[idx]['value']
        return None

    @app.callback(Output('preformated-data-{}'.format(i), 'children'),
                  [Input('run-selector-{}'.format(i), 'value')],
                  [State('tab-data', 'data')])
    def dropdown_callback(selected_run, data_args):
        if data_args is None or selected_run is None:
            return 'No run selected'
        return logic_manager.get_configs_from_ids(data_args['db'], [selected_run])
