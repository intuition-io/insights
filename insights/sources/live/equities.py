#
# Copyright 2013 Xavier Bruhiere
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


import pandas as pd

from intuition.zipline.data_source import LiveDataFactory
import intuition.data.remote as remote


class EquitiesLiveSource(LiveDataFactory):
    """
    At each event datetime of the provided index, EquitiesLiveSource fetchs
    live data from google finance api.
    """
    data = remote.Data()

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'change': (float, 'perc_change'),
            'volume': (int, 'volume'),
        }

    def get_data(self):
        snapshot = self.data.fetch_equities_snapshot(symbols=self.sids,
                                                     level=1)
        if snapshot.empty:
            raise ValueError('no equities data available')
        #FIXME We need volume field to be consistent with the API
        row = {}
        for sid in snapshot.columns:
            row[sid] = {'volume': 1000}
        return snapshot.append(pd.DataFrame(row))
