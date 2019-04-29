import pymongo
import gridfs
from bson.objectid import ObjectId


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
            return info['contentType'].startswith('image')

        # retrieving all artifacts
        cursor = self.get_artifacts_info_from_ids(db_name, selected_ids)

        images = {}
        for exp in cursor:

            # new images data structure
            images_exp = {}
            for artifact in exp['artifacts']:
                id = str(artifact['file_id'])
                images_exp[id] = artifact['name']

            # remove non-image artifacts
            ids = [ObjectId(id) for id in images_exp.keys()]
            cursor = self.get_artifacts(db_name, ids)
            for (id, name), info in zip(images_exp.items(), cursor):
                if not is_image(info):
                    del images_exp[id]

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
