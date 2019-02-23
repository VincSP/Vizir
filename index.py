import json
from app import app, columns, generate_table_rows
from back import get_experience, init_connection_to_runs, on_load_database_options
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State

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

    html.Div(id='intermediate-value', style={'display': 'none'}),

    #Select experiences
    html.Div([
        html.Div('Select experiences'),
        html.Div(dcc.Dropdown(id='experience-selector', multi=True))
    ]),


    #Button to update table
    html.Div([
        html.Button(id='submit-button', n_clicks=0, children='Submit'),
    ]),



        html.Div([
            dcc.Input(
                id='editing-columns-name',
                placeholder='Enter a column name...',),
        html.Button('Add Column', id='editing-columns-button',)
        ]),

        # Match Table
        html.Div(
            dash_table.DataTable(id='table',
                                 columns=[{"name": '.'.join(col), "id": '.'.join(col)} for col in columns],
                                 row_selectable="multi",
                                 selected_rows=[],
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
        html.Div(id='inter-value', style={'display': 'none'}, children=[]),
        html.Button('Submit', id='editing-datatable',),
        html.Div(
            dash_table.DataTable(id='sec_table',
                                 columns=[{"name": '.'.join(col), "id": '.'.join(col)} for col in columns],
                                 row_deletable=True,
                                 style_cell_conditional=[
                                                            {
                                                                'if':{'row_index' : 'odd'},
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


@app.callback(Output('intermediate-value', 'children'),
              [Input('database-selector', 'value')])
def update_list_experience(selected_database):
    exps = get_experience(selected_database)
    experience_options = ([{'label': exp, 'value': exp} for exp in exps])
    print(experience_options)
    return json.dumps(experience_options)


@app.callback(Output('experience-selector', 'options'),
              [Input('intermediate-value', 'children')])
def inter_dropdown_connection(value):
    return json.loads(value)

'''
Update datatable. Program wait State arg before fire callback
 and populate the table.
'''
@app.callback(Output('table', 'data'),
              [Input('submit-button', 'n_clicks'), Input('editing-columns-button','n_clicks')],
              [State('database-selector', 'value'),
                State('experience-selector', 'value'),
                State('editing-columns-name', 'value'),
               State('table', 'data')
               ])
def update_table(n_clicks, v_clicks, selected_database, selected_experience, new_col, data):
    if selected_database is None:
        return []
    global columns
    collection = init_connection_to_runs(selected_database)
    cursor = collection.find({'experiment.name': {'$in': selected_experience}})
    if new_col is not None:
        columns += [new_col.split('.')]
    rows = generate_table_rows(cursor, columns)

    return rows

@app.callback(Output('table', 'columns'),
              [Input('editing-columns-button','n_clicks')],
              [State('editing-columns-name', 'value'),
                State('table', 'columns'),
               State('table', 'data')])
def update_columns(v_clicks, value, cols, data):
    if v_clicks is None:
        return cols

    if v_clicks > 0:
        cols.append({
            'id': value, 'name': value,
            'editable_name': True, 'deletable': True
        })
    return cols


@app.callback(Output('inter-value', 'children'),
              [Input('table', 'selected_rows'),
               Input('table', 'data')])
def update_sec_datatable_inter(rows,selected_rows_id):
    selected_rows =[selected_rows_id[i] for i in rows]
    return json.dumps(selected_rows)


@app.callback(Output('sec_table', 'data'),
              [Input('editing-datatable','n_clicks')],
              [
                  State('inter-value', 'children'),

              ])
def update_sec_datatable(click, value):
    rows = json.loads(value)
    return rows

if __name__ == '__main__':
    app.run_server(debug=True)