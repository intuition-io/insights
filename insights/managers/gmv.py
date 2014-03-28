# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import numpy as np
from intuition.api.portfolio import PortfolioFactory


def compute_weigths(daily_returns):
    try:
        #create a covariance matrix
        covariance_matrix = np.cov(daily_returns, y=None, rowvar=1,
                                   bias=0, ddof=None)
        covariance_matrix = np.matrix(covariance_matrix)

        #calculate global minimum portfolio weights
        one_vector = np.matrix(np.ones(len(daily_returns))).transpose()
        one_row = np.matrix(np.ones(len(daily_returns)))
        covariance_matrix_inv = np.linalg.inv(covariance_matrix)
        numerator = np.dot(covariance_matrix_inv, one_vector)
        denominator = np.dot(np.dot(one_row, covariance_matrix_inv),
                             one_vector)

        return numerator / denominator
    except Exception, error:
        print(error)
        return np.zeros(len(daily_returns))


# https://www.quantopian.com/posts/global-minimum-variance-portfolio?c=1
class GlobalMinimumVariance(PortfolioFactory):
    '''
    doc: Computes a suitable compromise between risks and returns on buy
      signals and gives up the stock on sell ones.

    parameters:
      partial_sale: Percentage of the stock amount to sell [default 1]
    '''
    def initialize(self, config):
        self.partial_sell = config.get('partial_sell', 1.0)

    def optimize(self, date, to_buy, to_sell, parameters):

        allocations = {}

        # Simply sell
        for sid in to_sell:
            # NOTE Cannot go short in this configuration
            allocations[sid] = - int(round(
                self.portfolio.positions[sid].amount * self.partial_sell))

        if to_buy:
            returns = parameters.get('historical_prices')
            # NOTE if returns.isnull().any().any(): ?
            if returns is None:
                # TODO A fallback
                raise NotImplementedError('GMV manager needs history prices')

            weights = compute_weigths(returns.transpose())
            if np.isnan(weights).any() or not weights.any():
                self.log.warning('Could not compute weigths')
            else:
                for i, sid in enumerate(returns):
                    allocations[sid] = float(weights[i])

        return allocations, 0, 1
