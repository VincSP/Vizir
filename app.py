import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

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


# start Flask server

if __name__ == '__main__':
    app.run_server(debug=True)





