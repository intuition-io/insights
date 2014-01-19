import numpy as np

from intuition.zipline.portfolio import PortfolioFactory
import insights.transforms as transforms


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
    Computes from data history a suitable compromise between risks and returns.
    '''
    def initialize(self, config):

        self.price_transform = transforms.get_past_prices(
            #refresh_period=10,
            window_length=config.get('window', 40),
            compute_only_full=config.get('only_full', True))

    def optimize(self, date, to_buy, to_sell, parameters):

        allocations = {}

        for sid in to_sell:
            allocations[sid] = - self.portfolio.positions[sid].amount

        if len(to_buy) > 0:
            if 'historical_prices' in parameters:
                returns = parameters['historical_prices']
            else:
                returns_df = self.price_transform.handle_data(to_buy)
                if returns_df is None:
                    # Not enough data yet
                    return allocations, 0, 1
                for i, column in enumerate(returns_df):
                    # Remove incomplete data
                    if returns_df[column].isnull().any():
                        returns_df = returns_df.dropna(axis=1)
                returns = returns_df.values

            weights = compute_weigths(returns.transpose())
            if np.isnan(weights).any() or not weights.any():
                self.log.warning('Could not compute weigths')
                allocations = {}
            else:
                for i, sid in enumerate(returns_df):
                    allocations[sid] = float(weights[i])

        return allocations, 0, 1
