# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Linear optimization strategies for portfolio  managers
  ------------------------------------------------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

from intuition.api.portfolio import PortfolioFactory


class Constant(PortfolioFactory):
    '''
    doc: Allocate a constant amount to every signals, regardless of the
      portfolio.<br \> The algorithm can dynamically change the parameters and
      also advise a "scale" value to each sid.
    parameters:
      buy_amount: Number of sid units to buy [default 100]
      sell_amount: Number of sid units to sell [default All]
    '''
    def initialize(self, configuration):
        self.log.debug(configuration)

    def optimize(self, to_buy, to_sell):
        '''
        Buy sid * parameters['buy_amount'] * parameters['scale'][sid]
        Sell sid * parameters['sell_amount'] * parameters['scale'][sid]
        '''
        allocations = {}

        # Process every stock the same way
        for s in to_buy:
            quantity = self.properties.get('buy_amount', 100)
            if s in self.properties.get('scale', {}):
                quantity *= self.properties['scale'][s]
            # Allocate defined amount to buy
            allocations[s] = int(quantity)

        # NOTE You must provide sell_amount if you want to short
        for s in to_sell:
            quantity = self.properties.get(
                'sell_amount', self.portfolio.positions[s].amount)
            if s in self.properties.get('scale', {}):
                quantity *= self.properties['scale'][s]
            # Allocate defined amount to buy
            allocations[s] = -int(quantity)

        # Defaults values
        e_ret = 0
        e_risk = 1
        return allocations, e_ret, e_risk


class Fair(PortfolioFactory):
    '''
    doc: Dispatch equal weigths for buy signals and give up everything on sell
      ones.
    '''
    def optimize(self, to_buy, to_sell):
        allocations = {}
        if to_buy:
            fraction = round(1.0 / float(len(to_buy)), 2)
            for s in to_buy:
                allocations[s] = fraction
        for s in to_sell:
            allocations[s] = - self.portfolio.positions[s].amount
        return allocations, 0, 1
