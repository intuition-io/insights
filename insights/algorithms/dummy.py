# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Dummy algorithms
  ----------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

import random
from intuition.api.algorithm import TradingFactory
import insights.transforms as transforms
from insights.algorithms.utils import common_middlewares


class BuyAndHold(TradingFactory):
    '''
    doc: Depending on the given parameters, this algorithm will buy every sids
      once or at regular intervals.
    parameters:
      start_time: Unique "buy signal".
        Ignored if equal or less than 0 [default 3]
      rate: Regular "buy signal", ignored if -1 [default -1]
    '''
    def initialize(self, properties):
        # Punctual buy signals, except 0 means never
        self.start_time = properties.get('start_time', 3)
        # regularly buy signals
        self.rate = properties.get('rate', -1)

        # Interactive, mobile, hipchat, database and commission middlewares
        for middleware in common_middlewares(properties, self.identity):
            self.use(middleware)

    def _check_rate(self):
        return (self.rate > 0) and (self.elapsed_time.days % self.rate == 0)

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        # One shot or always buying or regularly
        if self.elapsed_time.days == self.start_time \
                or self._check_rate():
            # Only cares about buying everything
            signals['buy'] = data

        return signals


class Random(TradingFactory):
    '''
    doc: Randomly choose for each sid to buy, sell or pass
    parameters:
      buy_trigger: Chances to buy [default 0.5 < x < 1]
      sell_trigger: Chances to sell [default 0 < x < 0.5]
    '''
    def initialize(self, properties):

        for middleware in common_middlewares(properties, self.identity):
            self.use(middleware)

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


# TODO Merge with buyandhold
# https://www.quantopian.com/posts/global-minimum-variance-portfolio?c=1
class RegularRebalance(TradingFactory):
    '''
    doc: Reconsidere the portfolio allocation regularly, providing to the
      portfolio strategy a moving window of quotes data.
    parameters:
      rate: Reallocation period [default 10]
      window: quotes window tracked [default 40]
    '''

    def initialize(self, properties):

        for middleware in common_middlewares(properties, self.identity):
            self.use(middleware)

        # Set Max and Min positions in security
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0

        # This is the lookback window that the entire algorithm depends on
        self.refresh_period = properties.get('rate', 10)
        self.returns_transform = transforms.get_past_returns(
            refresh_period=self.refresh_period,
            window_length=properties.get('window', 40),
            compute_only_full=True)

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        #get 20 days of prices for each security
        daily_returns = self.returns_transform.handle_data(data)

        #circuit breaker in case transform returns none
        #circuit breaker, only calculate every given rate
        if (daily_returns is None) or \
                (self.elapsed_time.days % self.refresh_period is not 0):
            return signals

        #reweight portfolio
        for sid in data:
            signals['buy'][sid] = data[sid]

        self.manager.advise(historical_returns=daily_returns)
        return signals
