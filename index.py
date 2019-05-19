import logging

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import time
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app, default_columns, logic_manager
from apps import config_viewer, datatable, plot_viewer, pareto, plot_trajectory
import helpers

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('dashvision.index')

app.layout = html.Div([
    # Storages
    dcc.Store(id='database-dd-storage', storage_type='session'),
    dcc.Store(id='experiments-dd-storage', storage_type='session'),
    dcc.Store(id='table-columns-storage', storage_type='session'),
    dcc.Store(id='table-selection-storage', storage_type='session'),
    dcc.Store(id='plot-storage', storage_type='session'),
    dcc.Store(id='x-pareto-storage', storage_type='session'),
    dcc.Store(id='y-pareto-storage', storage_type='session'),
    dcc.Store(id='traj-id-storage', storage_type='session'),
    dcc.Store(id='steps-storage', storage_type='session'),

    # Page header
    html.Div([
        html.H1('Vizir')
    ]),

    # Select database
    html.Div([
        html.Div('Select DataBase'),
        html.Div(dcc.Dropdown(id='database-selector',
                              options=logic_manager.database_options()))
    ]),

    # Select experiments
    html.Div([
        html.Div('Select experiments'),
        html.Div(dcc.Dropdown(id='experiment-selector', multi=True))
    ]),
    html.Div([
        dcc.Input(
            id='add-column',
            placeholder='Enter a column name...', ),
    ]),
    html.Div([
        dcc.Input(
            id='add-query',
            placeholder='Enter a query...',),
    ]),
    # Match Table
    html.Div(
        dash_table.DataTable(id='experiment-table',
                             columns=[{"name": col, "id": col} for col in default_columns],
                             row_selectable="multi",
                             selected_rows=[],
                             sorting=True,
                             sorting_type="multi",                               
                             filtering=True,
                             style_table={
                                 'maxHeight': '300',
                                 'overflowY': 'scroll'
                             },
                             style_cell_conditional=[
                                                        {
                                                            'if': {'row_index': 'odd'},
                                                            'backgroundColor': 'rgb(248, 248, 248)'
                                                        }
                                                    ] + [
                                                        {
                                                            'if': {'id': col},
                                                            'textAlign': 'left'
                                                        } for col in ['name']
                                                    ],
                             )
    ),
    html.Button('Submit', id='update-selected-runs'),

    html.Div(
        [
            html.H1('Views'),
            dcc.Tabs(
                id="tabs",
                value='tab-datatable',
                children=[
                    dcc.Tab(label='Datatable', value='tab-datatable'),
                    dcc.Tab(label='Configs', value='tab-config'),
                    dcc.Tab(label='Graph', value='tab-graph'),
                    dcc.Tab(label='Pareto', value='tab-pareto'),
                    dcc.Tab(label='Trajectories', value='tab-trajectories'),
                ])],
        className="row"),
    html.Div(id='tab-content', className="row")],
    style={"margin": "2% 3%"})


@app.callback([Output('database-selector', 'value'),
               Output('experiment-selector', 'options')],
              [Input('database-dd-storage', 'modified_timestamp')],
              [State('database-selector', 'options'),
               State('database-dd-storage', 'data')])
def select_or_load_db(ts, db_options, stored_db_name):
    if ts is None:
        # Stored data isn't loaded yet.
        raise PreventUpdate

    if stored_db_name is None or not helpers.selection_in_options(stored_db_name, db_options):
        # Stored database is not an available option
        return None, []

    exps_selector_options = logic_manager.experiment_options(stored_db_name)
    return stored_db_name, exps_selector_options


@app.callback(Output('database-dd-storage', 'data'),
              [Input('database-selector', 'value')],
              [State('database-dd-storage', 'modified_timestamp')])
def select_database(selected_value, ts):
    """
    Stores the database selected by the user in the session storage.
    """
    if ts is None:
        raise PreventUpdate
    return selected_value


@app.callback(Output('experiment-selector', 'value'),
              [Input('experiment-selector', 'options')],
              [State('experiments-dd-storage', 'data'),
               State('experiments-dd-storage', 'modified_timestamp')])
def init_experiments(exp_options, stored_experiments, ts):
    if ts is None:
        raise PreventUpdate

    if helpers.selection_in_options(stored_experiments, exp_options):
        return stored_experiments

    return None


@app.callback(Output('experiments-dd-storage', 'data'),
              [Input('experiment-selector', 'value')],
               # Input('table-selection-storage', 'data')],
              [State('experiments-dd-storage', 'modified_timestamp')])
def select_experiement(selected_value, ts):
    """
    Stores the experiments selected by the user in the session storage.
    """
    if ts is None:
        raise PreventUpdate

    return selected_value


@app.callback(Output('experiment-table', 'data'),
              [Input('experiment-selector', 'value'),
               Input('table-columns-storage', 'data'),
               Input('add-query', 'n_submit'),
               Input('database-selector', 'value')],
              [State('add-query', 'value')])
def update_experiment_table(experiment_names, cols, query_nsub, db_name, query):
    '''
    Update datatable. Program wait State arg before fire callback
     and populate the table.
    '''
    if db_name is None or not experiment_names:
        return []

    columns = [col['id'] for col in cols]
    rows = logic_manager.table_content_from_exp_names(db_name, experiment_names, columns)

    if query_nsub is not None:
        rows = logic_manager.filter_rows_by_query(rows, query)

    return rows


@app.callback(Output('table-columns-storage', 'data'),
              [Input('add-column', 'n_submit'),
               Input('experiment-table', 'columns')],
              [State('add-column', 'value'),])
def save_columns(n_submit, cols, value):
    ctx = dash.callback_context
    adding_column = any(itm['prop_id'] == 'add-column.n_submit' for itm in ctx.triggered)

    if adding_column:
        if n_submit is None:
            raise PreventUpdate
        if n_submit > 0:
            cols.append({
                'id': value, 'name': value,
                'editable_name': True, 'deletable': True
            })
    return cols


@app.callback(Output('experiment-table', 'columns'),
              [Input('table-columns-storage', 'modified_timestamp')],
              [State('table-columns-storage', 'data'),
               State('experiment-table', 'columns')])
def update_columns(ts, storage_cols, cols):
    # Use the default initial value if the storage is empty
    return storage_cols or cols


@app.callback(Output('tab-content', 'children'),
              [Input('tabs', 'value'),
               Input('update-selected-runs', 'n_clicks')])
def render_content(tab, update_clicks):
    if tab == 'tab-datatable':
        return datatable.layout
    elif tab == 'tab-config':
        return config_viewer.layout
    elif tab == 'tab-graph':
        return plot_viewer.layout
    elif tab == 'tab-pareto':
        return pareto.layout
    elif tab == 'tab-trajectories':
        return plot_trajectory.layout
    else:
        return html.Div('Not Found')


@app.callback(Output('tab-data', 'data'),
              [Input('tab-content', 'children'),
               Input('update-selected-runs', 'n_clicks')],
              [State('database-selector', 'value'),
               State('experiment-table', 'selected_rows'),
               State('experiment-table', 'data')])
def populate_hidden(tab, update_clicks, db_name, selected_rows, table_data):
    if db_name is None:
        logger.warning('No database selected')
        raise PreventUpdate

    selected_ids = sorted([table_data[i]['_id'] for i in selected_rows])
    return {
        'db': db_name,
        'selected_ids': selected_ids,
    }


@app.callback(Output('table-selection-storage', 'data'),
              [Input('experiment-table', 'selected_rows'),
               Input('experiment-selector', 'value'),
               Input('add-query', 'n_submit')],
              [State('experiment-table', 'data'),
               State('database-selector', 'value'),
               State('table-selection-storage', 'data'),
               State('add-query', 'value')])
def reset_selected_rows(selected_rows, experiment_names, submit_query, table_data, db_name, stored_data, query_txt):
    #todo: Reset rows only if query_txt has changed
    ctx = dash.callback_context
    is_query = any(itm['prop_id'] == 'add-query.n_submit' for itm in ctx.triggered)

    stored_data = stored_data or {}
    logger.debug('Triggered by {}'.format(ctx.triggered))
    if is_query or db_name != stored_data.get('db_name') or experiment_names != stored_data.get('experiment_names'):
        if is_query:
            logger.debug('Reset because query')
        elif db_name != stored_data.get('db_name'):
            logger.debug('Reset because current db is {} and stored is {}'
                         .format(db_name, stored_data.get('db_name')))
        elif experiment_names != stored_data.get('experiment_names'):
            logger.debug('Reset because current db is {} and stored is {}'
                         .format(experiment_names, stored_data.get('experiment_names')))
        stored_data = {
            'db_name': db_name,
            'experiment_names': experiment_names,
            'selected_rows': []
        }
    else:
        stored_data['selected_rows'] = selected_rows
    return stored_data


@app.callback(Output('experiment-table', 'selected_rows'),
              [Input('table-selection-storage', 'modified_timestamp'),
              Input('experiment-selector', 'value')],
              [State('table-selection-storage', 'data')])
def load_selected_rows(ts, exp_selection, data):
    if ts is None or data is None:
        raise PreventUpdate
    return data['selected_rows']


if __name__ == '__main__':
    app.run_server(debug=True)
