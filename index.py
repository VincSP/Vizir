import logging

import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app, default_columns, data_manager
from apps import config_viewer, datatable

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('dashvision.index')

app.layout = html.Div([

    # Page header
    html.Div([
        html.H1('Dash Vision')
    ]),

    # Select database
    html.Div([
        html.Div('Select DataBase'),
        html.Div(dcc.Dropdown(id='database-selector',
                              options=data_manager.on_load_database_options()))
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
                    dcc.Tab(label='Configs', value='tab-config')])],
        className="row"),
    html.Div(id='tab-content', className="row")],
    style={"margin": "2% 3%"})


@app.callback(Output('experiment-selector', 'options'),
              [Input('database-selector', 'value')])
def update_list_experiment(db_name):
    exp_names = data_manager.get_experiment_names(db_name)
    exps_selector_options = ([{'label': name, 'value': name} for name in exp_names])
    return exps_selector_options


@app.callback(Output('experiment-table', 'data'),
              [Input('experiment-selector', 'value'),
                Input('experiment-table', 'columns'),
                Input('add-query', 'n_submit')],
              [State('add-query', 'value'),
                State('database-selector', 'value')])
def update_experiment_table(experiment_names, cols, query_nsub, query, db_name):
    '''
    Update datatable. Program wait State arg before fire callback
     and populate the table.
    '''
    if db_name is None:
        return []

    columns = [col['id'] for col in cols]
    rows = data_manager.get_table_content_from_exp_names(db_name, experiment_names, columns)

    if query_nsub is not None:
        rows = data_manager.filter_rows_by_query(rows, query)

    return rows


@app.callback(Output('experiment-table', 'columns'),
              [Input('add-column', 'n_submit')],
              [State('add-column', 'value'),
               State('experiment-table', 'columns')])
def update_columns(n_submit, value, cols):
    if n_submit is None:
        return cols

    if n_submit > 0:
        cols.append({
            'id': value, 'name': value,
            'editable_name': True, 'deletable': True
        })
    return cols


@app.callback(Output('tab-content', 'children'),
              [Input('tabs', 'value'),
               Input('update-selected-runs', 'n_clicks')])
def render_content(tab, update_clicks):
    if tab == 'tab-datatable':
        return datatable.layout
    elif tab == 'tab-config':
        return config_viewer.layout
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


if __name__ == '__main__':
    app.run_server(debug=True)
