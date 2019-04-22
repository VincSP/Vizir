import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go


from dash.dependencies import Input, Output, State

from app import app, default_columns, logic_manager

layout = html.Div([
    html.H3('Plot'),
    html.Div(id='tab-data', style={'display': 'none'}),
    html.Div(dcc.Dropdown(id='metric-dropdown')),
    html.Div(
        dcc.Graph(id='metric-plot')
    ),
    dcc.Interval(
            id='graph-interval',
            interval=5000,
            n_intervals=0
        )

])


@app.callback(Output('metric-dropdown', 'options'),
              [Input('tab-data', 'data')])
def populate_metric_dropdown(data_args):
    if data_args is None:
        return []
    selected_ids = data_args.get('selected_ids', [])
    db_name = data_args['db']
    metric_names = logic_manager.metric_names_from_ids(db_name, selected_ids)
    return [{'label': name, 'value': name} for name in metric_names]


@app.callback(Output('metric-plot', 'figure'),
              [Input('metric-dropdown', 'value'),
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

    traces = []
    for d in metric_data:
        trace = go.Scatter(
            x=d['steps'],
            y=d['values'],
            name=d['run_id'],
        )
        traces.append(trace)

    fig = go.Figure(data=traces, layout=layout)

    return fig