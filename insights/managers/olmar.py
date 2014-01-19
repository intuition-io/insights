import numpy as np

from intuition.zipline.portfolio import PortfolioFactory
import insights.managers.utils as utils


class OLMAR(PortfolioFactory):
    '''
    On-Line Portfolio Moving Average Reversion

    More info can be found in the corresponding paper:
    http://icml.cc/2012/papers/168.pdf
    '''

    initialized = False

    def initialize(self, configuration):
        self.log.debug(configuration)
        self.eps = configuration.get('eps', 1)

    def _warming(self, data):
        self.m = len(data.keys())
        self.b_t = np.ones(self.m) / self.m

    def _rebalance_portfolio(self, data, desired_port):
        # rebalance portfolio
        allocations = {}
        desired_amount = np.zeros_like(desired_port)
        current_amount = np.zeros_like(desired_port)
        prices = np.zeros_like(desired_port)

        if not self.initialized:
            positions_value = self.portfolio.starting_cash
            self.initialized = True
        else:
            positions_value = self.portfolio.positions_value + \
                self.portfolio.cash

        for i, stock in enumerate(data):
            current_amount[i] = self.portfolio.positions[stock].amount
            prices[i] = data[stock].price

        desired_amount = np.round(desired_port * positions_value / prices)

        diff_amount = desired_amount - current_amount

        for i, stock in enumerate(data):
            # Remove nan values
            if not np.isnan(diff_amount[i]):
                allocations[stock] = int(diff_amount[i])
        return allocations

    def optimize(self, date, to_buy, to_sell, parameters):
        # This implementation only process buy signals
        data = to_buy

        if not self.initialized:
            self._warming(data)

        x_tilde = np.zeros(self.m)
        b = np.zeros(self.m)

        # find relative moving average price for each security
        for i, stock in enumerate(data):
            price = data[stock].price
            # Relative mean deviation
            if 'mavg' in data[stock]:
                x_tilde[i] = data[stock]['mavg']['price'] / price

        ###########################
        # Inside of OLMAR (algo 2)
        x_bar = x_tilde.mean()

        # market relative deviation
        mark_rel_dev = x_tilde - x_bar

        # Expected return with current portfolio
        exp_return = np.dot(self.b_t, x_tilde)
        weight = self.eps - exp_return
        variability = (np.linalg.norm(mark_rel_dev)) ** 2

        # test for divide-by-zero case
        if variability == 0.0:
            step_size = 0
        else:
            step_size = max(0, weight / variability)

        b = self.b_t + step_size * mark_rel_dev
        b_norm = utils.simplex_projection(b)
        np.testing.assert_almost_equal(b_norm.sum(), 1)

        allocations = self._rebalance_portfolio(data, b_norm)

        # update portfolio
        self.b_t = b_norm

        #e_ret = 0
        #e_risk = 1
        e_ret = exp_return
        e_risk = variability
        return allocations, e_ret, e_risk
