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


import random
import zipline.finance.commission as commission

from intuition.zipline.algorithm import TradingFactory
import insights.transforms as transforms
import insights.plugins.database as database
import insights.plugins.mobile as mobile
import insights.plugins.messaging as msg


class BuyAndHold(TradingFactory):
    '''
    Buy every sids on the given day, regularly or always (start_day = -1), and
    until the end
    '''
    def initialize(self, properties):
        # Punctual buy signals, with -1 for always, 0 never
        self.start_day = properties.get('start_day', 2)
        # regularly buy signals
        self.rate = properties.get('rate', -1)

        if properties.get('interactive'):
            self.use(msg.RedisProtocol(self.identity).check)
        device = properties.get('notify')
        if device:
            self.use(mobile.AndroidPush(device).notify)
        if properties.get('save'):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        self.set_commission(commission.PerTrade(
            cost=properties.get('commission', 2.5)))

    def _check_rate(self):
        return (self.rate > 0) and (self.days % self.rate == 0)

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        # One shot or always buying or regularly
        if self.days == self.start_day \
                or self.start_day < 0 \
                or self._check_rate():
            # Only cares about buying everything
            signals['buy'] = data

        return signals


class Random(TradingFactory):
    '''
    Randomly choose to buy or sell
    '''
    def initialize(self, properties):

        if properties.get('interactive'):
            self.use(msg.RedisProtocol(self.identity).check)
        device = properties.get('notify')
        if device:
            self.use(mobile.AndroidPush(device).notify)
        if properties.get('save'):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        self.set_commission(commission.PerTrade(
            cost=properties.get('commission', 2.5)))

        self.buy_trigger = properties.get(
            'buy_trigger', random.randint(500, 1000) / 1000.0)
        self.sell_trigger = properties.get(
            'sell_trigger', random.randint(0, 500) / 1000.0)

        # Makes results reproductible
        random.seed(self.identity)

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        # One shot or always buying or regularly
        for sid in data:
            luck = random.random()
            if luck >= self.buy_trigger:
                signals['buy'][sid] = data[sid]
            elif luck <= self.sell_trigger:
                signals['sell'][sid] = data[sid]

        return signals


# https://www.quantopian.com/posts/global-minimum-variance-portfolio?c=1
class RegularRebalance(TradingFactory):
    '''
    Reconsidere the portfolio allocation every <refresh_period> periods,
    providing to the portfolio strategy <window_length> days of quote data.
    '''

    def initialize(self, properties):

        if properties.get('interactive'):
            self.use(msg.RedisProtocol(self.identity).check)
        device = properties.get('notify')
        if device:
            self.use(mobile.AndroidPush(device).notify)
        if properties.get('save'):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        # Set Max and Min positions in security
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0

        self.set_commission(commission.PerTrade(
            cost=properties.get('commission', 2.5)))

        # This is the lookback window that the entire algorithm depends on
        self.refresh_period = properties.get('refresh', 10)
        self.returns_transform = transforms.get_past_returns(
            refresh_period=self.refresh_period,
            window_length=properties.get('window', 40),
            compute_only_full=True)

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        #get 20 days of prices for each security
        daily_returns = self.returns_transform.handle_data(data)

        #circuit breaker in case transform returns none
        #circuit breaker, only calculate every 10 days
        if (daily_returns is None) or \
                (self.days % self.refresh_period is not 0):
            return signals

        #reweight portfolio
        for sid in data:
            signals['buy'][sid] = data[sid]

        self.manager.advise(historical_returns=daily_returns)
        return signals
