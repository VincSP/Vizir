import dash

# get_nested(d, keys) create a list of key : value

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


columns = [('_id',), ('status',)]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
