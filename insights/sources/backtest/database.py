#
# Copyright 2014 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from insights.plugins.database import RethinkdbBackend


def remove_extention(sid):
    dot_pos = sid.find('.')
    return sid[:dot_pos] if dot_pos > 0 else sid


class RethinkdbPrices(object):
    '''
    Get quotes from Rethinkdb database
    '''
    select = 'close'

    def __init__(self, data_descriptor):
        self.db = RethinkdbBackend(
            db=data_descriptor.get('database', 'quotes'))

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'volume': (int, 'volume'),
        }

    def get_data(self, sids, start, end):
        #TODO Use 'adjusted_close'
        return self.db.quotes(sids,
                              start=start,
                              end=end,
                              select=self.select)
