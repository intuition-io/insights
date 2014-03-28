# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Standard deviation based algorithm
  ----------------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

from intuition.api.algorithm import TradingFactory


# https://www.quantopian.com/posts/auto-adjusting-stop-loss
class AutoAdjustingStopLoss(TradingFactory):

    stocks = {}

    def initialize(self, properties):
        # Interactive, mobile, hipchat, database and commission middlewares
        self.use_default_middlewares(properties)

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}
        scale = {}

        for sid in data:
            current_price = data[sid].price
            r_o_r = 0

            #Check if this stock is already in portfolio
            #if sid in self.portfolio.positions.keys():
            if sid in self.stocks:
                # Check if the sell price needs to be updated
                purchase_price = self.portfolio.positions[sid].cost_basis
                if purchase_price > 0:
                    r_o_r = (current_price - purchase_price) / purchase_price
                    sell_price = (1 - ((-r_o_r * .05) + .10)) * current_price

                    if r_o_r > 1.5:
                        if (.9 * r_o_r) > self.stocks[sid]:
                            self.stocks[sid] = (.9 * r_o_r)

                    elif r_o_r > 1:
                        if (1.8 * purchase_price) > self.stocks[sid]:
                            self.stocks[sid] = 1.8 * purchase_price
                        signals['buy'][sid] = data[sid]
                        scale[sid] = 1

                    elif r_o_r > .5:
                        if (1.35 * purchase_price) > self.stocks[sid]:
                            self.stocks[sid] = 1.35 * purchase_price
                        signals['buy'][sid] = data[sid]
                        scale[sid] = 2

                    elif r_o_r > .15:
                        if (1.05 * purchase_price) > self.stocks[sid]:
                            self.stocks[sid] = 1.05 * purchase_price
                        signals['buy'][sid] = data[sid]
                        scale[sid] = 3

                    elif r_o_r > .05:
                        if (.95 * purchase_price) > self.stocks[sid]:
                            self.stocks[sid] = .95 * purchase_price
                        signals['buy'][sid] = data[sid]
                        scale[sid] = 4

                    if self.stocks[sid] > current_price:
                        signals['sell'][sid] = data[sid]
                        scale[sid] = 1
            else:
                signals['buy'][sid] = data[sid]
                scale[sid] = 1
                sell_price = .85 * current_price
                self.stocks[sid] = sell_price

        self.manager.advise(scale=scale)
        return signals
