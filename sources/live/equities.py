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


import sys
import logbook

from intuition.zipline.data_source import DataFactory
from intuition.data.remote import Remote


log = logbook.Logger('intuition.sources.live.equities')


class EquitiesLiveSource(DataFactory):
    """
    At each event datetime of the provided index, EquitiesLiveSource fetchs
    live data from google finance api.
    """
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
        snapshot = self.remote.fetch_equities_snapshot(symbols=self.sids,
                                                       level=1)
        if snapshot.empty:
            log.error('** No data available, maybe stopped by google ?')
            sys.exit(2)
        return snapshot

    def raw_data_gen(self):
        self.remote = Remote()
        index = self._get_updated_index()
        for dt in index:
            self._wait_for_dt(dt)
            snapshot = self.get_data()

            for sid in self.sids:
                #NOTE Conversions here are useless ?
                if snapshot[sid]['perc_change'] == '':
                    snapshot[sid]['perc_change'] = 0
                event = {
                    'dt': dt,
                    'sid': sid,
                    'price': float(snapshot[sid]['last_price'][1:]),
                    'perc_change': float(snapshot[sid]['perc_change']),
                    #FIXME No volume available with level 1 or None
                    #TODO Here just a special value that the algo could detect
                    #     like a missing data
                    'volume': 10001,
                }
                yield event
