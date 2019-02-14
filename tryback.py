import pymongo
import pandas as pd
import dash
import dash_table
from flask import Flask
from flask.json import JSONEncoder
from bson import json_util
from mongoengine.base import BaseDocument
from mongoengine.queryset.base import BaseQuerySet
from bson import ObjectId
from bson.json_util import dumps
import json
import os
from pandas.io.json import json_normalize



client = pymongo.MongoClient('drunk:27017')

database = client["arthur_exp_database"]

collection = database["runs"]


cursor = collection.find_one({'experiment.name':'grid_search_patch_celebA'})
from pprint import pprint
pprint(cursor)

exit()
cursor = collection.find({'experiment.name':'grid_search_patch_celebA'})

#print([(k, type(v)) for k, v in cursor.items()])
data = [cursor]
columns = [['_id'], ['status'], ['config', 'dataset', 'name']]
def generate_table_rows(cursor, columns):
    for exp in cursor:
        for col in columns:
            val = get_recursive(exp, col)
            '.'.join(col)


def get_recursive(d, keys):
    if len(keys) == 1:
        return d[keys[0]]
    return get_recursive(d[keys[0]], keys[1:])
keys = ['a', 'b']
print(get_recursive({"a":{'b':{"a":4, "c":2}}}, keys))
print(keys)

exit()
app = dash.Dash(__name__)
app.layout =dash_table.DataTable(id='table',
                                 columns=[{"name": i, "id": i} for i in columns],
                                 data=df.to_dict("rows"),
                                 )
if __name__ == '__main__':
    app.run_server(debug=True)







