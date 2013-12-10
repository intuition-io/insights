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


from intuition.zipline.algorithm import TradingFactory
from zipline.transforms import MovingAverage


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

    def handle_data(self, data):
        if self.debug:
            print('\n' + 79 * '=')
            print self.portfolio
            print(79 * '=' + '\n')

        ''' ---------------------------------------------------    Init   --'''
        if self.initialized:
            self.manager.update(
                self.portfolio,
                self.datetime.to_pydatetime(),
                self.perf_tracker.cumulative_risk_metrics.to_dict(),
                save=self.save,
                widgets=False)
            for t in data:
                self.invested[t] = False
        else:
            self.initialized = True
        signals = {}

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

        ''' ---------------------------------------------------   Orders  --'''
        if signals:
            orderBook = self.manager.trade_signals_handler(signals)
            for ticker in orderBook:
                if self.debug:
                    self.logger.notice('{} Ordering {} {} stocks'
                        .format(self.datetime, ticker, orderBook[ticker]))
                self.order(ticker, orderBook[ticker])

        # Save mavgs for later analysis.
        self.short_mavgs.append(short_mavg)
        self.long_mavgs.append(long_mavg)
