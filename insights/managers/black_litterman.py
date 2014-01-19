''' ****************************************************
    EXPERIMENTAL
**************************************************** '''


from numpy import dot
from numpy.linalg import inv
import numpy as np

from intuition.zipline.portfolio import PortfolioFactory
import insights.managers.utils as utils
import insights.transforms as transforms

# rf is the risk-free rate
rf = 0.015
# tau is a scalar indicating the uncertainty in the CAPM prior
tau = 0.025
# Assumes 255 trading days per year
trading_days_per_year = 255


class BlackLitterman(PortfolioFactory):
    '''
    https://www.quantopian.com/posts/black-litterman

    This algorithm performs a Black-Litterman portfolio construction. The
    framework is built on the classical mean-variance approach, but allows the
    investor to specify views about the over- or under- performance of various
    assets.  Uses ideas from the Global Minimum Variance Portfolio algorithm
    posted on Quantopian. Ideas also adopted from
    www.quantandfinancial.com/2013/08/portfolio-optimization-ii-black.html.

    window gives the number of data points that are extracted from historical
    data to estimate the expected returns and covariance matrix.
    '''

    days = 0

    def initialize(self, configuration):
        # window gives the number of data points that are extracted
        # from historical data
        # to estimate the expected returns and covariance matrix.
        self.window = configuration.get('window', trading_days_per_year)
        self.refresh_rate = configuration.get('refresh', 10)
        #TODO Automatically find out
        # Apple, Google, GE, Microsoft, Amazon
        self.market_cap = [479.51, 377.58, 272.76, 300.86, 180.96]
        self.cap_wts = \
            np.array(self.market_cap) / sum(np.array(self.market_cap))

        self.only_full = configuration.get('only_full', True)
        self.price_transform = transforms.get_past_prices(
            refresh_period=self.refresh_rate,
            window_length=self.window,
            compute_only_full=self.only_full)

    def optimize(self, date, to_buy, to_sell, parameters):
        allocations = {}
        #TODO Not sure about that
        #NOTE How can I merge those two:
        #to_buy.update(to_sell)
        data = to_buy
        self.days += 1

        adapt_window = self.window \
            if (self.only_full and (self.days >= self.window)) \
            else self.days

        # Get 'adapt_window' days of prices for each security
        all_prices = self.price_transform.handle_data(data)

        # Circuit breaker in case transform returns none
        # and only calculate every 20 days
        if (all_prices is None) or (self.days % self.refresh_rate is not 0):
            return {}, 0, 1

        # Compute daily returns
        daily_returns = np.zeros((len(data), adapt_window))
        for i, security in enumerate(data):
            for day in range(0, adapt_window):
                day_of = all_prices[security][day]
                day_before = all_prices[security][day-1]
                daily_returns[i][day] = (day_of-day_before) / day_before

        expreturns, covars = utils.assets_meanvar(daily_returns)

        new_mean = utils.compute_mean(self.cap_wts, expreturns)
        new_var = utils.compute_var(self.cap_wts, covars)

        # Compute implied equity risk premium
        lmb = (new_mean - rf) / new_var
        # Compute equilibrium excess returns
        Pi = dot(dot(lmb, covars), self.cap_wts)

        # Solve for weights before incorporating views
        weights = utils.solve_weights(Pi+rf, covars, rf)

        # calculate tangency portfolio
        mean, var = utils.compute_mean(weights, expreturns), \
            utils.compute_var(weights, covars)

        #TODO Experimental interactive algorithm
        # VIEWS ON ASSET PERFORMANCE Here, we give two views, that Google will
        # outperform Apple by 3%, and that Google will outperform Microsoft by
        # 2%.
        P = np.array([[1, -1, 0, 0, 0], [1, 0, -1, 0, 0]])
        Q = np.array([0.03, 0.02])

        # omega represents the uncertainty of our views. Rather than specify
        # the 'confidence' in one's view explicitly, we extrapolate an implied
        # uncertainty from market parameters.
        omega = dot(dot(dot(tau, P), covars), np.transpose(P))

        # Compute equilibrium excess returns
        # taking into account views on assets
        sub_a = inv(dot(tau, covars))
        sub_b = dot(dot(np.transpose(P), inv(omega)), P)
        sub_c = dot(inv(dot(tau, covars)), Pi)
        sub_d = dot(dot(np.transpose(P), inv(omega)), Q)
        Pi_new = dot(inv(sub_a + sub_b), (sub_c + sub_d))
        # Perform a mean-variance optimization taking into account views

        new_weights = utils.solve_weights(Pi_new + rf, covars, rf)

        leverage = sum(abs(new_weights))
        portfolio_value = (
            self.portfolio.positions_value + self.portfolio.cash) / leverage

        # Re-weight portfolio
        for i, security in enumerate(data):
            current_position = self.portfolio.positions[security].amount
            new_position = (portfolio_value * new_weights[i]) / \
                all_prices[security][adapt_window-1]

            #FIXME I dont know why if fails with certain securities
            if not np.isnan(new_position):
                allocations[security] = int(new_position - current_position)

        e_ret = 0
        e_risk = 1
        return allocations, e_ret, e_risk
