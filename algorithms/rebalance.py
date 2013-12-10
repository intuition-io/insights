#
# Copyright 2012 Xavier Bruhiere
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


import numpy as np

from zipline.transforms import batch_transform

from intuition.zipline.algorithm import TradingFactory


# https://www.quantopian.com/posts/global-minimum-variance-portfolio?c=1
class RegularRebalance(TradingFactory):
    '''
    For this example, we're going to write a simple momentum script.  When
    the stock goes up quickly, we're going to buy; when it goes down quickly,
    we're going to sell.  Hopefully we'll ride the waves.
    '''

    def initialize(self, properties):

        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)

        # This is the lookback window that the entire algorithm depends on
        self.refresh_period = properties.get('refresh_period', 10)
        self.returns_transform = get_past_returns(
            refresh_period=self.refresh_period,
            window_length=properties.get('window_length', 40),
            compute_only_full=False)

        #Set day
        self.day = 0

        # Set Max and Min positions in security
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0
        #Set commission
        #self.set_commission(commission.PerTrade(cost=7.95))

    def handle_data(self, data):

        self.day += 1

        if self.debug:
            print('\n' + 79 * '=')
            print self.portfolio
            print(79 * '=' + '\n')

        if self.initialized:
            self.manager.update(
                self.portfolio,
                self.datetime,
                self.perf_tracker.cumulative_risk_metrics.to_dict(),
                save=self.save,
                widgets=False)
        else:
            # Perf_tracker need at least a turn to have an index
            self.initialized = True

        signals = {}

        #get 20 days of prices for each security
        daily_returns = self.returns_transform.handle_data(data)

        #circuit breaker in case transform returns none
        if daily_returns is None:
            return
        #circuit breaker, only calculate every 20 days
        if self.day % self.refresh_period is not 0:
            return

        #reweight portfolio
        for i, sid in enumerate(data):
            signals[sid] = data[sid].price

        self.process_signals(signals, historical_prices=daily_returns)

    def process_signals(self, signals, **kwargs):
        if not signals:
            return

        order_book = self.manager.trade_signals_handler(
            signals, kwargs)

        for sid in order_book:
            if self.debug:
                self.logger.notice('{} Ordering {} {} stocks'
                    .format(self.datetime, sid, order_book[sid]))
            self.order(sid, order_book[sid])


@batch_transform
def get_past_returns(data):
    '''
    Parameters: data
        pandas.panel (major: index, minor: sids)
    '''
    returns_df = data['price'].pct_change()
    #returns_df = returns_df.fillna(0.0)
    # Because of return calculation, first raw is nan
    #FIXME nan values remain anyway
    return np.nan_to_num(returns_df.values[1:])
