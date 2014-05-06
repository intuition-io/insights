# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Signal Generators
  -----------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import collections
import zipline.transforms.ta as ta
import insights.transforms as transforms
import insights.plugins.mail as mail
from intuition.api.algorithm import TradingFactory
from insights.algorithms.utils import common_middlewares


class RSIWithMA(TradingFactory):
    '''
    doc: |
      Use The Relative Strengh Indicator to detect signals<br \>
        - RSI < 70% => sell<br \>
        - RSI > 30% => buy<br \>
      Then check Long and Short Moving averages to confirm:<br />
        - Process if MAs are getting closer'
    parameters:
      buy_trigger: Low percent of the RSI [default 30]
      sell_trigger: High percent of the RSI [default 70]
      period: RSI computation period of time [default 14]
      window: Quote history loopback to provide to the manager [default 40]
      only_full: Start when we have a full window of quotes [default false]
    '''

    over_priced = {}
    under_priced = {}

    def initialize(self, properties):
        # Interactive, mobile, hipchat, database and commission middlewares
        for middleware in common_middlewares(properties, self.identity):
            self.use(middleware)

        report_mails = properties.get('reports')
        if report_mails:
            self.use(mail.Report(report_mails).send_briefing)

        self.buy_trigger = properties.get('buy_trigger', 30)
        self.sell_trigger = properties.get('sell_trigger', 70)
        self.period = properties.get('period', 14)

        # RSI Signal
        self.rsi = ta.RSI(timeperiod=self.period)

        # Quotes loopback for managers
        self.prices_transform = transforms.get_past_prices(
            #refresh_period=10,
            window_length=properties.get('window', 40),
            compute_only_full=properties.get('only_full'))

    def warm(self, data):
        self.over_priced = {sid: False for sid in data}
        self.under_priced = {sid: False for sid in data}

    def event(self, data):
        self.logger.debug('Processing event on {}'.format(self.get_datetime()))
        signals = {}

        rsi_data = self.rsi.handle_data(data)
        loopback_prices = self.prices_transform.handle_data(data)
        if rsi_data.isnull().any() or (loopback_prices is None):
            return signals

        self.manager.advise(historical_prices=loopback_prices)
        self.logger.debug('Historical data available')

        ranked = {}
        banked = {}
        for sid in data:
            rsi = rsi_data[sid]
            if rsi < self.sell_trigger and self.over_priced[sid]:
                banked[sid] = rsi
                self.over_priced[sid] = False

            elif rsi > self.sell_trigger \
                    and not self.over_priced[sid]:
                self.over_priced[sid] = True

            elif rsi > self.buy_trigger and self.under_priced[sid]:
                ranked[sid] = rsi
                self.under_priced[sid] = False

            elif rsi < self.buy_trigger \
                    and not self.under_priced[sid]:
                self.under_priced[sid] = True

        signals['buy'] = collections.OrderedDict(
            {sid: data[sid] for sid, _ in sorted(
                ranked.items(), key=lambda t: t[1])})
        signals['sell'] = collections.OrderedDict(
            {sid: data[sid] for sid, _ in sorted(
                banked.items(), key=lambda t: t[1])})

        return signals
