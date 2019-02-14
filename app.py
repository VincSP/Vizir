import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pymongo
client = pymongo.MongoClient('drunk:27017')

#############################
# Data Manipulation / Model
#############################


def get_database_name():

    dbl = client.list_database_names()
    return dbl


def get_experience(selected_database):
    db = client[selected_database]
    collection = db["runs"]
    list = []
    for x in collection.find({}, {'experiment.name': 1}).distinct('experiment.name'):
        list.append(x)
    return list

def get_nested(d, keys):
    if len(keys) == 1:
        return d[keys[0]]
    return get_nested(d[keys[0]], keys[1:])

def generate_table_rows(cursor, columns):
    rows = []
    for exp in cursor:
        row = {}
        for col in columns:
            row['.'.join(col)] = get_nested(exp, col)
            rows.append(row)
    return rows


columns = [('_id',), ('status',), ('config', 'dataset', 'name')]

########################################################################################################################
# Dashboard Layout / View
########################################################################################################################

def onLoad_database_options():
    database_options = (
        [{'label': database, 'value': database}
         for database in get_database_name()]
    )
    return database_options


app = dash.Dash()
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([

    #Page header

    html.Div([
        html.H1('Dash Vision')
    ]),

    #Select database

    html.Div([
        html.Div([
            html.Div('Select DataBase'),
            html.Div(dcc.Dropdown(id='database-selector',
                                  options=onLoad_database_options()))
        ]),



    #Select experiences
        html.Div([
            html.Div('Select experiences'),
            html.Div(dcc.Dropdown(id='experience-selector', multi=True))
        ]),
    ]),

    html.Div([

            # Match Table
            html.Div(
                dash_table.DataTable(id='table',
                                     columns=[{"name": '.'.join(col), "id": '.'.join(col)} for col in columns],)
            )
    ])
])

#######################################################################################################################
# Interaction Between Components / Controller
#######################################################################################################################

#update dropdown experiences


@app.callback(Output('experience-selector', 'options'),
              [Input('database-selector', 'value')])
def update_list_experience(selected_database):
    exps = get_experience(selected_database)
    experience_options = ([{'label': exp, 'value': exp} for exp in exps])
    return experience_options


@app.callback(Output('table', 'data'),
              [Input('database-selector', 'value')]
              [Input('experience-selector', 'value')])
def update_table(selected_database, selected_experience):
    db = client[selected_database]
    collection = db[selected_experience]
    cursor = collection.find({'experiment.name': str(selected_experience)})
    rows = generate_table_rows(cursor, columns)
    return rows



# start Flask server

if __name__ == '__main__':
    app.run_server(debug=True)





