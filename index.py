import logging

import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State

from app import app, columns
from back import get_experiment_names, on_load_database_options, get_table_content

logging.basicConfig(level=logging.DEBUG)


app.layout = html.Div([

    #Page header
    html.Div([
        html.H1('Dash Vision')
    ]),

    #Select database
    html.Div([
        html.Div('Select DataBase'),
        html.Div(dcc.Dropdown(id='database-selector',
                                options=on_load_database_options()))
    ]),

    #Select experiments
    html.Div([
        html.Div('Select experiments'),
        html.Div(dcc.Dropdown(id='experiment-selector', multi=True))
    ]),


    #Button to update table
    html.Div([
        html.Button(id='generate-experiment-table-button', n_clicks=0, children='Submit'),
    ]),


    html.Div([
        dcc.Input(
            id='editing-columns-name',
            placeholder='Enter a column name...',),
    html.Button('Add Column', id='editing-columns-button',)
    ]),

    # Match Table
    html.Div(
        dash_table.DataTable(id='experiment-table',
                             columns=[{"name": col, "id": col} for col in columns],
                             row_selectable="multi",
                             selected_rows=[],
                             filtering=True,
                             style_table={
                                    'maxHeight':'300',
                                    'overflowY' :'scroll'
                             },
                             style_cell_conditional=[
                                                        {
                                                            'if':{'row_index' : 'odd'},
                                                            'backgroundColor' : 'rgb(248, 248, 248)'
                                                        }
                                                    ] + [
                                 {
                                     'if': {'id': col},
                                     'textAlign': 'left'
                                 } for col in ['name']
                             ],
                             )
    ),
    html.Button('Submit', id='editing-datatable'),
    html.Div(
        dash_table.DataTable(id='tmp_table',
                             columns=[{"name": col, "id": col} for col in columns],
                             row_deletable=True,
                             style_cell_conditional=[
                                                        {
                                                            'if': {'row_index' : 'odd'},
                                                            'backgroundColor' : 'rgb(248,248,248)'
                                                        }
                                                    ] + [
                                 {
                                     'if':{'id' : col},
                                     'textAlign':'left'
                                 } for col in ['name']
                             ]
                             )
    )
])


@app.callback(Output('experiment-selector', 'options'),
              [Input('database-selector', 'value')])
def update_list_experiment(db_name):
    exp_names = get_experiment_names(db_name)
    exps_selector_options = ([{'label': name, 'value': name} for name in exp_names])
    return exps_selector_options


@app.callback(Output('experiment-table', 'data'),
              [Input('generate-experiment-table-button', 'n_clicks'),
                Input('experiment-table', 'columns')],
              [State('database-selector', 'value'),
                State('experiment-selector', 'value'),
                State('experiment-table', 'data')])
def update_experiment_table(n_clicks, cols, db_name, experiment_names, data):
    '''
    Update datatable. Program wait State arg before fire callback
     and populate the table.
    '''
    if db_name is None:
        return []

    columns = [col['id'] for col in cols]
    rows = get_table_content(db_name, experiment_names, columns)
    return rows


@app.callback(Output('experiment-table', 'columns'),
              [Input('editing-columns-button','n_clicks')],
              [State('editing-columns-name', 'value'),
                State('experiment-table', 'columns')])
def update_columns(v_clicks, value, cols):
    if v_clicks is None:
        return cols

    if v_clicks > 0:
        cols.append({
            'id': value, 'name': value,
            'editable_name': True, 'deletable': True
        })
    return cols


@app.callback(Output('tmp_table', 'data'),
              [Input('editing-datatable','n_clicks')],
               [State('experiment-table', 'data'),
                State('experiment-table', 'selected_rows')])
def update_sec_datatable_inter(click, rows, selected_rows_id):
    return [rows[i] for i in selected_rows_id]


if __name__ == '__main__':
    app.run_server(debug=True)
