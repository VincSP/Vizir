import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go


from dash.dependencies import Input, Output, State

from app import app, default_columns, logic_manager

layout = html.Div([
    html.H3('Plot Aggr'),
    html.Div(id='tab-data', style={'display': 'none'}),
    html.Div(dcc.Dropdown(id='metric-aggr-dropdown')),
    html.Div(
        dcc.Graph(id='metric-aggr-plot')
    ),
    dcc.Interval(
            id='graph-interval',
            interval=5000,
            n_intervals=0
        )
])


@app.callback(Output('metric-aggr-dropdown', 'options'),
              [Input('tab-data', 'data')])
def populate_metric_dropdown(data_args):
    if data_args is None:
        return []
    selected_ids = data_args.get('selected_ids', [])
    db_name = data_args['db']
    metric_names = logic_manager.metric_names_from_ids(db_name, selected_ids)
    return [{'label': name, 'value': name} for name in sorted(metric_names)]


@app.callback(Output('metric-aggr-plot', 'figure'),
              [Input('metric-aggr-dropdown', 'value'),
               Input('graph-interval', 'n_intervals')],
              [State('tab-data', 'data')])
def plot_metric(metric_name, n, data_args):
    if data_args is None:
        return []
    selected_ids = data_args.get('selected_ids', [])
    db_name = data_args['db']
    metric_data = logic_manager.metric_data_from_ids(metric_name, db_name, selected_ids)

    layout = go.Layout(
        title=metric_name,
    )

    data = {}
    for exp in metric_data:
        for s, v in zip(exp['steps'], exp['values']):
            if s not in data:
                data[s] = [v]
            else:
                data[s] += [v]

    traces = []
    for x, y in sorted(data.items()):
        trace = go.Box(
            y=y,
            name=f'{x}:{len(y)}',
        )
        traces.append(trace)

    fig = go.Figure(data=traces, layout=layout)

    return fig