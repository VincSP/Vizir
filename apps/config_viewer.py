
import dash_html_components as html
import dash_table



def get_tab_content():
    layout = html.Div([
            html.H3('Datatabl of selected runs'),
            html.Div(
                dash_table.DataTable(id='selected_datatable',
                                     columns=[{"name": col, "id": col} for col in default_columns],
                                     data=data,
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