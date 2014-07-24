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
            self.use(middleware['func'], middleware['backtest'])
        report_mails = properties.get('reports')
        if report_mails:
            self.use(mail.Report(report_mails).send_briefing, False)

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
        recorded_state = {}

        for sid in data:
            short_mavg = data[sid].short_mavg['price']
            long_mavg = data[sid].long_mavg['price']
            recorded_state[sid] = {
                'price': data[sid].price,
                'signals': {
                    'short': short_mavg,
                    'long': long_mavg
                }
            }

            if short_mavg - long_mavg > self.threshold \
                    and not self.invested[sid]:
                signals['buy'][sid] = data[sid]
                self.invested[sid] = True
                recorded_state[sid]['msg'] = (
                    'Buy {}: short ma crossed up threshold ({} - {} > {})'
                    .format(sid, short_mavg, long_mavg, self.threshold)
                )

            elif short_mavg - long_mavg < -self.threshold \
                    and self.invested[sid]:
                signals['sell'][sid] = data[sid]
                self.invested[sid] = False
                recorded_state[sid]['msg'] = (
                    'Sell {}: short ma crossed down threshold ({} - {} < {})'
                    .format(sid, short_mavg, long_mavg, self.threshold)
                )

        self.record(**recorded_state)
        return signals
