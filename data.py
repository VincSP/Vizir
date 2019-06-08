import os
import pickle
import shutil
import tempfile

import gridfs
import pymongo
import gridfs
from bson.objectid import ObjectId

import torch


class MongoManager():
    def __init__(self, server='localhost', port='27017'):
        self._client = pymongo.MongoClient(server, int(port))

    def get_database_names(self, ):
        '''Get all databases on MongoDB'''
        dbl = self._client.list_database_names()
        return dbl

    def init_connection_to_runs(self, db_name):
        '''Generic function to access directly to runs collection of selected database'''
        db = self._client[db_name]
        return db['runs']
    
    def init_connection_to_fsfiles(self, db_name):
        '''Generic function to access directly to fs.files collection of selected database'''
        db = self._client[db_name]
        return db['fs.files']

    def init_connection_to_gridfs(self, db_name):
        db = self._client[db_name]
        return gridfs.GridFS(db)

    def init_connection_to_metrics(self, db_name):
        db = self._client[db_name]
        return db['metrics']

    def init_connection_to_gridfs(self, db_name):
        '''Generic function to access directly to runs collection of selected database'''
        db = self._client[db_name]
        return gridfs.GridFS(db)

    def get_experiment_names(self, db_name):
        ''''
        Returns a list of experiments of selected data_base

        :param db_name:
        :return:
        '''
        if db_name is None:
            return []
        collection = self.init_connection_to_runs(db_name)
        exp_names = collection.find({}, {'experiment.name': 1}).distinct('experiment.name')
        return exp_names

    def get_rows_from_exp_names(self, db_name, exp_names, columns):
        collection = self.init_connection_to_runs(db_name)

        filter = {'experiment.name': {'$in': exp_names}}
        projection = dict((col, True) for col in columns)

        cursor = collection.find(filter=filter, projection=projection)

        return cursor

    def get_rows_from_ids(self, db_name, selected_ids, columns):
        collection = self.init_connection_to_runs(db_name)
        filter = {'_id': {'$in': selected_ids}, }
        projection = dict((col, True) for col in columns)
        cursor = collection.find(filter=filter, projection=projection)
        return cursor

    def get_configs_from_ids(self, db_name, selected_ids):
        collection = self.init_connection_to_runs(db_name)
        filter = {'_id': {'$in': selected_ids}, }
        projection = dict(config=True)
        cursor = collection.find(filter=filter, projection=projection)
        return cursor

    def get_images_from_ids(self, db_name, selected_ids):
        """
            returns dictionary of 
            {
                selected_id: {
                    image_id: image_name
                }
            }
        """
        def is_image(info):
            if 'contentType' in info:
                return info['contentType'].startswith('image')
            elif 'content-type' in info['metadata']:
                return info['metadata']['content-type'].startswith('image')
            else:
                return False

        # retrieving all artifacts
        cursor = self.get_artifacts_info_from_ids(db_name, selected_ids)

        images = {}
        for exp in cursor:

            # new images data structure
            artifacts_exp = {}
            for artifact in exp['artifacts']:
                id = str(artifact['file_id'])
                artifacts_exp[id] = artifact['name']

            # remove non-image artifacts
            ids = [ObjectId(id) for id in artifacts_exp.keys()]
            cursor = self.get_artifacts(db_name, ids)
            images_exp = {}
            for (id, name), info in zip(artifacts_exp.items(), cursor):
                if is_image(info):
                    images_exp[id] = name

            images[exp['_id']] = images_exp

        return images

    def get_file(self, db_name, file_id):
        fs = self.init_connection_to_gridfs(db_name)
        conn = fs.get(ObjectId(file_id))
        bytes = conn.read()
        conn.close()
        return bytes

    def get_artifacts_info_from_ids(self, db_name, selected_ids):
        collection = self.init_connection_to_runs(db_name)
        filter = {'_id': {'$in': selected_ids}, }
        projection = {'artifacts': 1}
        cursor = collection.find(filter=filter, projection=projection)
        return cursor

    def get_artifacts(self, db_name, file_ids):
        collection = self.init_connection_to_fsfiles(db_name)
        filter = {'_id': {'$in': file_ids}}
        cursor = collection.find(filter=filter)
        return cursor

    def get_from_run_info(self, attr, db_name, run_id):
        collection = self.init_connection_to_runs(db_name)
        filter = {"_id": run_id}
        projection = {"info.{}".format(attr): 1}
        return collection.find_one(filter=filter, projection=projection)['info'][attr]

    def get_from_runs_infos(self, attr, db_name, selected_ids):
        collection = self.init_connection_to_runs(db_name)
        filter = {"_id": {"$in": selected_ids}}
        projection = {"info.{}".format(attr): 1}
        return collection.find(filter=filter, projection=projection)

    def get_metrics_infos(self, db_name, selected_ids):
        return self.get_from_runs_infos('metrics', db_name, selected_ids)

    def get_metric_data(self, metric_name, db_name, selected_ids):
        collection = self.init_connection_to_metrics(db_name)
        filter = {"name": {"$eq": metric_name}, "run_id": {"$in": selected_ids}}
        cursor = collection.find(filter=filter)
        return cursor

    def get_metrics_data(self, metric_names, db_name, selected_ids):
        collection = self.init_connection_to_metrics(db_name)
        filter = {"name": {"$in": metric_names}, "run_id": {"$in": selected_ids}}
        cursor = collection.find(filter=filter)
        return cursor

    def get_artifact_id_from_name(self, artifact_name, db_name, run_id):
        collection = self.init_connection_to_runs(db_name)
        exp = collection.find_one({"_id": run_id, 'artifacts.name': artifact_name}, {'artifacts': 1})
        if exp is None:
            return None

        for elt in exp['artifacts']:
            if elt['name'] == artifact_name:
                return elt['file_id']

    def get_artifact(self, db_name, artifact_name, selected_id):
        object_id = self.get_artifact_id_from_name(artifact_name, db_name, selected_id)
        artifact = self.init_connection_to_gridfs(db_name).get(object_id)
        temp_path = tempfile.mkdtemp()
        temp_file = os.path.join(temp_path, 'salut')
        with open(temp_file, 'wb') as f:
            f.write(artifact.read())
            obj = torch.load(temp_file)
        shutil.rmtree(temp_path)
        return obj
