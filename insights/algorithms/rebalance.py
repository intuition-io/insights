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


import numpy as np

from zipline.transforms import batch_transform

from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database


# https://www.quantopian.com/posts/global-minimum-variance-portfolio?c=1
class RegularRebalance(TradingFactory):
    '''
    Reconsidere the portfolio allocation every <refresh_period> periods,
    providing to the portfolio strategy <window_length> days of quote data.
    '''

    def initialize(self, properties):

        if properties.get('save', False):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        # This is the lookback window that the entire algorithm depends on
        self.refresh_period = properties.get('refresh_period', 10)
        self.returns_transform = get_past_returns(
            refresh_period=self.refresh_period,
            window_length=properties.get('window_length', 40),
            compute_only_full=False)

        # Set Max and Min positions in security
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0
        #Set commission
        #self.set_commission(commission.PerTrade(cost=7.95))

    def event(self, data):
        signals = {}

        #get 20 days of prices for each security
        daily_returns = self.returns_transform.handle_data(data)

        #circuit breaker in case transform returns none
        if daily_returns is None:
            return {}
        #circuit breaker, only calculate every 20 days
        if self.day % self.refresh_period is not 0:
            return {}

        #reweight portfolio
        for sid in data:
            signals[sid] = data[sid].price

        self.manager.advise(historical_prices=daily_returns)
        return signals


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
