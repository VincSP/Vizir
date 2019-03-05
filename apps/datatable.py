import dash_html_components as html
import dash_table

from dash.dependencies import Input, Output, State

from app import app, default_columns

layout = html.Div([
    html.H3('Datatable of selected runs'),
    html.Div(id='tab-data', style={'display': 'none'}),
    html.Div(
        dash_table.DataTable(
            id='selected_datatable',
            columns=[{"name": col, "id": col} for col in default_columns],
            row_deletable=True,
            style_cell_conditional=[
                                       {
                                           'if': {'row_index': 'odd'},
                                           'backgroundColor': 'rgb(248,248,248)'
                                       }
                                   ] + [
                                       {
                                           'if': {'id': col},
                                           'textAlign': 'left'
                                       } for col in ['name']
                                   ]
        )
    )
])

@app.callback(Output('selected_datatable', 'data'), [Input('tab-data', 'data')])
def populate_table(data_args):
    print(data_args)
    return []
