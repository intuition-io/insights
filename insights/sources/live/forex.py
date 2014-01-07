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


import time
import logbook
import pandas as pd

from intuition.zipline.data_source import LiveDataFactory
from intuition.data.forex import ConnectTrueFX


log = logbook.Logger('intuition.sources.live.forex')


class ForexLiveSource(LiveDataFactory):
    """
    At each event datetime of the provided index, ForexLiveSource fetchs live
    forex data from TrueFX.
    Supported universe is as follow
    EUR/USD  USD/JPY  GBP/USD  EUR/GBP  USD/CHF  EUR/JPY  EUR/CHF  USD/CAD
    AUD/USD  GBP/JPY  AUD/JPY  AUD/NZD  CAD/JPY  CHF/JPY  NZD/USD
    """
    def initialize(self, data_descriptor, **kwags):
        self.forex = ConnectTrueFX(pairs=self.sids)

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            #TODO Here conversion (weird result for now)
            # Or: (lambda x: pd.tslib.i8_to_pydt(x + '000000'), 'trade_time'),
            'trade_time': (lambda x: pd.datetime.utcfromtimestamp(
                float(x[:-3])), 'TimeStamp'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'Bid.Price'),
            'ask': (float, 'Ask.Price'),
            'high': (float, 'High'),
            'low': (float, 'Low'),
            'volume': (int, 'volume')
        }

    def get_data(self):
        while True:
            rates = self.forex.query_trueFX()
            if len(rates.keys()) >= len(self.sids):
                log.info('New income data, fire an event !')
                log.debug('Data available:\n{}'.format(rates))
                break
            log.debug('Waiting for Forex update')
            time.sleep(30)
        #FIXME We need volume field to be consistent with the API
        row = {}
        for sid in rates.columns:
            row[sid] = {'volume': 1000}
        return rates.append(pd.DataFrame(row))
