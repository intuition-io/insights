# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Etcd context
  ------------

  Fetch the configuration from ectd cluster.
  https://github.com/coreos/etcd
  It needs an input like :
  <1.2.3.4:port/doc_id>

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

# Can't make python-etcd to work currently
import etcd
from intuition.api.context import ContextFactory


class EtcdContext(ContextFactory):

    def initialize(self, storage):
        # storage = {{ etcd_ip }}:{{ etcd_port }}/{{ conf_id }}
        etcd_ip = storage['uri'].split(':')[0]
        etcd_port = int(storage['uri'].split(':')[1])
        self.conf_id = storage['path'][0]
        self.client = etcd.Client(host=etcd_ip, port=etcd_port)

    def load(self):
        #TODO A beautiful recursive function
        context = {}
        for item in self.client.get('/' + self.conf_id):
            key_1 = item.key.split('/')[-1]
            if item.dir:
                context[key_1] = {}
                for subitem in self.client.get(item.key):
                    context[key_1][subitem.key.split('/')[-1]] = subitem.value
            else:
                context[key_1] = item.value

        return context
