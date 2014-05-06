# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Moving average based algorithms
  -------------------------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

from zipline.transforms import MovingAverage
import insights.plugins.mail as mail
from intuition.api.algorithm import TradingFactory
from insights.algorithms.utils import common_middlewares


class DualMovingAverage(TradingFactory):
    '''
    doc: Buys once its short moving average crosses its long moving average
      (indicating upwards momentum) and sells its shares once the averages
      cross again (indicating downwards momentum).
    parameters:
      long_window: Long window of data to track for moving average computation.
        [default 30]
      short_window: Short window of data to track for moving average
        computation. [default 0.5*long_window]
      short_rate: Alternative to short_window parameter.
        Set short window length as a fraction of the long one. [default 0.5]
      threshold: Distance between moving averages to trigger signal [default 0]
    '''
    def initialize(self, properties):
        # Interactive, mobile, hipchat, database and commission middlewares
        for middleware in common_middlewares(properties, self.identity):
            self.use(middleware)
        report_mails = properties.get('reports')
        if report_mails:
            self.use(mail.Report(report_mails).send_briefing)

        long_window = int(properties.get('long_window', 30))
        short_window = int(properties.get('short_window', 0))
        if not short_window:
            short_window = int(round(
                properties.get('ma_rate', 0.5) * float(long_window), 2))
        self.threshold = properties.get('threshold', 0)

        self.add_transform(MovingAverage, 'short_mavg', ['price'],
                           window_length=short_window)

        self.add_transform(MovingAverage, 'long_mavg', ['price'],
                           window_length=long_window)

        # To keep track of whether we invested in the stock or not
        self.invested = {}
        self.short_mavgs = []
        self.long_mavgs = []

    def warm(self, data):
        self.invested = {sid: False for sid in data}

    def event(self, data):
        self.logger.debug('Processing event on {}'.format(self.get_datetime()))
        signals = {'buy': {}, 'sell': {}}

        for ticker in data:
            short_mavg = data[ticker].short_mavg['price']
            long_mavg = data[ticker].long_mavg['price']

            if short_mavg - long_mavg > self.threshold \
                    and not self.invested[ticker]:
                signals['buy'][ticker] = data[ticker]
                self.invested[ticker] = True

            elif short_mavg - long_mavg < -self.threshold \
                    and self.invested[ticker]:
                signals['sell'][ticker] = data[ticker]
                self.invested[ticker] = False

        return signals


# https://www.quantopian.com/posts/this-is-amazing
'''
class Momentum(TradingFactory):
    # FIXME Too much transactions, can't handle it on wide universe
    def initialize(self, properties):
        # Interactive, mobile, hipchat, database and commission middlewares
        for middleware in common_middlewares(properties, self.identity):
            self.use(middleware)

        self.max_notional = 2000.1
        self.min_notional = -2000.0

        self.max_weight = properties.get('max_weight', 0.2)
        self.max_exposure = properties.get('max_exposure', self.max_weight)

        self.add_transform(MovingAverage, 'mavg', ['price'],
                           window_length=properties.get('window', 3))

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        for ticker in data:
            sma = data[ticker].mavg.price
            price = data[ticker].price
            cash = self.portfolio.cash
            notional = self.portfolio.positions[ticker].amount * price
            capital_used = self.portfolio.capital_used

            if sma > price and \
                    notional > -self.max_exposure * (capital_used + cash):
                signals['sell'][ticker] = data[ticker]
            elif sma < price and \
                    notional < self.max_weight * (capital_used + cash):
                signals['buy'][ticker] = data[ticker]

        return signals
'''
