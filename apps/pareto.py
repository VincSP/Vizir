import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go


from dash.dependencies import Input, Output, State

from app import app, default_columns, logic_manager

layout = html.Div([
    html.H3('Pareto'),
    html.Div(id='tab-data', style={'display': 'none'}),
    html.Div(dcc.Dropdown(id='x-metric-dropdown')),
    html.Div(dcc.Dropdown(id='y-metric-dropdown')),
    html.Div(
        dcc.Graph(id='pareto-plot')
    ),
    html.Div(id='result'),
    dcc.Interval(
            id='graph-interval',
            interval=500000,
            n_intervals=0
        )

])


@app.callback([Output('x-metric-dropdown', 'options'),
               Output('x-metric-dropdown', 'value')],
              [Input('tab-data', 'data')],
              [State('x-pareto-storage', 'data')])
def populate_x_dropdown(data_args, x_pareto_storage_data):
    if data_args is None:
        return []
    selected_ids = data_args.get('selected_ids', [])
    db_name = data_args['db']
    metric_names = logic_manager.metric_names_from_ids(db_name, selected_ids)
    return [{'label': name, 'value': name} for name in metric_names], x_pareto_storage_data

@app.callback([Output('y-metric-dropdown', 'options'),
               Output('y-metric-dropdown', 'value')],
              [Input('tab-data', 'data')],
              [State('y-pareto-storage', 'data')])
def populate_y_dropdown(data_args, y_pareto_storage_data):
    if data_args is None:
        return []
    selected_ids = data_args.get('selected_ids', [])
    db_name = data_args['db']
    metric_names = logic_manager.metric_names_from_ids(db_name, selected_ids)
    return [{'label': name, 'value': name} for name in metric_names], y_pareto_storage_data


@app.callback(Output('x-pareto-storage', 'data'),
              [Input('x-metric-dropdown', 'value')],)
def store_selected_x_metric(selected_metric):
    return selected_metric


@app.callback(Output('y-pareto-storage', 'data'),
              [Input('y-metric-dropdown', 'value')],)
def store_selected_y_metric(selected_metric):
    return selected_metric

@app.callback(Output('result', 'children'),
              [Input('x-metric-dropdown', 'value'),
               Input('y-metric-dropdown', 'value'),
               Input('graph-interval', 'n_intervals')],
              [State('tab-data', 'data')])
def display_selection(x_metric_name, y_metric_name, n, data_args):
    return '{} in function of {}'.format(y_metric_name, x_metric_name)


@app.callback(Output('pareto-plot', 'figure'),
              [Input('x-metric-dropdown', 'value'),
               Input('y-metric-dropdown', 'value'),
               Input('graph-interval', 'n_intervals')],
              [State('tab-data', 'data')])
def plot_pareto(x_metric_name, y_metric_name, n, data_args):
    if data_args is None:
        return []
    selected_ids = data_args.get('selected_ids', [])
    db_name = data_args['db']
    return logic_manager.get_pareto_curves(x_metric_name, y_metric_name, db_name, selected_ids)
