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
from intuition.api.data_source import DataFactory


def remove_extention(sid):
    dot_pos = sid.find('.')
    return sid[:dot_pos] if dot_pos > 0 else sid


#class RethinkdbOHLC(RethinkdbPrices):
class RethinkdbOHLC(DataFactory):
    '''
    Get quotes from Rethinkdb database
    '''

    select = 'ohlc'

    def initialize(self, data_descriptor, **kwargs):
        self.db = RethinkdbBackend(db='quotes')

        if self.sids[0] == 'random':
            # --universe random[,4]
            count = int(self.sids[1]) if (len(self.sids) == 2) else 10
            self.sids = self.db.random_tables(count)
        else:
            self.sids = map(remove_extention, self.sids)

    @property
    def mapping(self):
        #FIXME Some NaN values survice so far
        mapping = {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'close'),
            'volume': (int, 'volume'),
        }
        # Add additional fields.
        for field_name in self.data.minor_axis:
            if field_name in ['close', 'volume', 'dt', 'sid']:
                continue
            mapping[field_name] = (lambda x: x, field_name)
        return mapping

    def get_data(self):
        data = self.db.quotes(self.sids,
                              start=self.start,
                              end=self.end,
                              select=self.select)
        # Unknown data were poped from dataframe
        self.sids = data.items
        return data
