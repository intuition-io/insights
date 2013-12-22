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


from zipline.transforms import MovingAverage

from intuition.zipline.algorithm import TradingFactory
import intuition.modules.plugins.database as database


class DualMovingAverage(TradingFactory):
    '''
    Buys once its short moving average crosses its long moving average
    (indicating upwards momentum) and sells its shares once the averages cross
    again (indicating downwards momentum).
    '''
    def initialize(self, properties):
        self.save = properties.get('save', False)
        long_window = properties.get('long_window', 400)
        short_window = properties.get('short_window', None)
        if short_window is None:
            short_window = int(round(
                properties.get('ma_rate', 0.5) * float(long_window), 2))
        self.threshold = properties.get('threshold', 0)
        self.debug = properties.get('debug', 0)

        self.add_transform(MovingAverage, 'short_mavg', ['price'],
                           window_length=short_window)

        self.add_transform(MovingAverage, 'long_mavg', ['price'],
                           window_length=long_window)

        # To keep track of whether we invested in the stock or not
        self.invested = {}

        self.short_mavgs = []
        self.long_mavgs = []

    def preamble(self, data):
        if self.save:
            self.db = database.RethinkdbBackend(self.manager.name, True)
        for t in data:
            self.invested[t] = False

    def event(self, data):
        signals = {}
        self.logger.debug('Processing event {}'.format(self.datetime))

        import ipdb; ipdb.set_trace()
        if self.save and self.day >= 2:
            self.db.save_portfolio(self.datetime, self.portfolio)
            self.db.save_metrics(
                self.datetime, self.perf_tracker.cumulative_risk_metrics)

        ''' ---------------------------------------------------    Scan   --'''
        for ticker in data:
            short_mavg = data[ticker].short_mavg['price']
            long_mavg = data[ticker].long_mavg['price']
            if short_mavg - long_mavg > self.threshold \
                    and not self.invested[ticker]:
                signals[ticker] = data[ticker].price
                self.invested[ticker] = True
            elif short_mavg - long_mavg < -self.threshold \
                    and self.invested[ticker]:
                signals[ticker] = - data[ticker].price
                self.invested[ticker] = False

        return signals
