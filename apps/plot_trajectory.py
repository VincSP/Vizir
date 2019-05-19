import dash_html_components as html
import dash_core_components as dcc


from dash.dependencies import Input, Output, State

from app import app, logic_manager

layout = html.Div([
    html.H3('Trajectory visualization'),
    html.Div(id='tab-data', style={'display': 'none'}),
    html.Div(dcc.Dropdown(id='ids-dropdown')),
    html.Div(dcc.Dropdown(id='steps-dropdown')),
    html.Div(
        dcc.Graph(id='traj-plot')
    ),

    dcc.Interval(
            id='graph-interval',
            interval=60000,
            n_intervals=0
        )

])


@app.callback([Output('ids-dropdown', 'options'),
               Output('ids-dropdown', 'value')],
              [Input('tab-data', 'data')],
              [State('traj-id-storage', 'data')]
              )
def populate_ids_dropdown(data_args, traj_id_storage_data):
    if data_args is None:
        return []
    selected_ids = data_args.get('selected_ids', [])
    return [{'label': name, 'value': name} for name in selected_ids], traj_id_storage_data

@app.callback([Output('steps-dropdown', 'options'),
               Output('steps-dropdown', 'value')],
              [Input('ids-dropdown', 'value')],
              [State('tab-data', 'data'),
              State('steps-storage', 'data')])
def populate_traj_dropdown(selected_id, data_args, storage_data):
    if selected_id is None:
        return []
    db_name = data_args['db']
    available_steps = logic_manager.traj_step_from_id_options(db_name, selected_id)
    return available_steps, storage_data


@app.callback(Output('traj-id-storage', 'data'),
              [Input('ids-dropdown', 'value')],)
def store_selected_traj_id(selected_id):
    return selected_id

@app.callback(Output('steps-storage', 'data'),
              [Input('steps-dropdown', 'value')],)
def store_selected_traj_id(selected_step):
    return selected_step

@app.callback(Output('traj-plot', 'figure'),
              [Input('steps-dropdown', 'value'),
               Input('graph-interval', 'n_intervals')],
              [State('ids-dropdown', 'value'),
                State('steps-dropdown', 'label '),
               State('tab-data', 'data')])
def plot_traj(step_idx, n, selected_id, step, data_args):
    if data_args is None:
        return []
    db_name = data_args['db']
    return logic_manager.get_trajectory_plot(step_idx, step, db_name, selected_id)
