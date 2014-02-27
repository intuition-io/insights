# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Mongodb context
  ---------------

  Fetch the configuration from mongo documents.
  It needs an input like :
  <1.2.3.4:port/database/collection/doc_id>

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

import pymongo
from intuition.errors import LoadContextFailed
from intuition.api.context import ContextFactory


# Super interface: http://genghisapp.com/
class MongodbContext(ContextFactory):

    def initialize(self, storage):
        if len(storage['path']) != 3:
            raise LoadContextFailed(
                driver=__name__,
                reason='you must provide a path like <db/collection/doc_id>')

        self.database = storage['path'][0]
        self.collection = storage['path'][1]
        self.conf_id = storage['path'][2]

        self.client = pymongo.MongoClient(
            "mongodb://{}/".format(storage['uri']))

    def _connect(self):
        if self.database not in self.client.database_names():
            raise LoadContextFailed(
                driver=__name__,
                reason='database {} not found'.format(self.database))
        return self.client[self.database]

    def _grab_doc(self, db):
        if self.collection not in db.collection_names():
            raise LoadContextFailed(
                driver=__name__,
                reason='collection {} not found'.format(self.collection))
        return db[self.collection]

    def load(self):
        db = self._connect()
        self.log.info('connected to {} database'.format(db.name))

        conf_doc = self._grab_doc(db)
        self.log.info('got {} document'.format(conf_doc.name))

        context = conf_doc.find_one({'id': self.conf_id})
        if not context:
            raise LoadContextFailed(
                driver=__name__,
                reason='document {} not found'.format(self.conf_id))

        return context
