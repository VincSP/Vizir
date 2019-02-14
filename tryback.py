import pymongo
import pandas as pd
import dash
import dash_table
from flask import Flask
from flask.json import JSONEncoder
from bson import json_util
# from mongoengine.base import BaseDocument
# from mongoengine.queryset.base import BaseQuerySet
from bson import ObjectId
from bson.json_util import dumps
import json
import os
from pandas.io.json import json_normalize
from pprint import pprint



client = pymongo.MongoClient('drunk:27017')

database = client["arthur_exp_database"]

collection = database["runs"]


# cursor = collection.find_one({'experiment.name':'grid_search_patch_celebA'})
# data = [cursor]
# pprint(cursor)

# exit()

def get_nested(d, keys):
    if len(keys) == 1:
        return d[keys[0]]
    return get_nested(d[keys[0]], keys[1:])

def generate_table_rows(cursor, columns):
    rows = []
    for exp in cursor:
        row = {}
        for col in columns:
            row[col] = get_nested(exp, col)
            rows.append(row)
    return rows

# keys = ['a', 'b']
# print(get_recursive({"a":{'b':{"a":4, "c":2}}}, keys))
# print(keys)
cursor = collection.find({'experiment.name':'grid_search_patch_celebA'})
columns = [('_id',), ('status',), ('config', 'dataset', 'name')]
rows = generate_table_rows(cursor, columns)
# pprint(rows)
# exit()
# import pandas as pd

# df = pd.read_csv('solar.csv')
# pprint(df.to_dict("rows"))
app = dash.Dash(__name__)
app.layout = dash_table.DataTable(id='table',
                                 columns=[{"name": '.'.join(col), "id": col} for col in columns],
                                 data=rows,
    # columns=[{"name": i, "id": i} for i in df.columns],
    # data=df.to_dict("rows"),                                 
                                 )
if __name__ == '__main__':
    app.run_server(debug=True)







