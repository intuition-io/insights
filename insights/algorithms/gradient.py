# encoding: utf-8
import random
import numpy as np

from zipline.transforms import batch_transform
import zipline.finance.commission as commission

from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database
import insights.plugins.messaging as messaging
import insights.plugins.mobile as mobile
#import insights.plugins.utils as utils


# https://www.quantopian.com/posts/\
# second-attempt-at-ml-stochastic-gradient-descent-\
# method-using-hinge-loss-function
class StochasticGradientDescent(TradingFactory):
    '''
    Randomly chooses training data, gradually decrease the learning rate, and
    penalize data points which deviate significantly from what's predicted.
    Here I used an average SGD method that is tested to outperform if I simply
    pick the last predictor value trained after certain iterations.
    '''
    def initialize(self, properties):
        #self.use(utils.debug_portfolio)
        if properties.get('interactive'):
            self.use(messaging.RedisProtocol(self.identity).check)
        device = properties.get('notify')
        if device:
            self.use(mobile.AndroidPush(device).notify)
        if properties.get('save'):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        self.rebalance_period = properties.get('rebalance_period', 5)

        self.bet_amount = self.capital_base
        self.max_notional = self.capital_base + 0.1
        self.min_notional = -self.capital_base
        self.gradient_iterations = properties.get('gradient_iterations', 5)
        self.calculate_theta = calculate_theta(
            refresh_period=properties.get('refresh', 1),
            window_length=properties.get('window', 60))

        self.set_commission(commission.PerTrade(
            cost=properties.get('commission', 2.5)))

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}
        scale = {}

        for stock in data:
            thetaAndPrices = self.calculate_theta.handle_data(
                data, stock, self.gradient_iterations)
            if thetaAndPrices is None:
                continue
            theta, historicalPrices = thetaAndPrices

            indicator = np.dot(theta, historicalPrices)
            # normalize
            hlen = sum([k * k for k in historicalPrices])
            tlen = sum([j * j for j in theta])
            # Makes the indicator lies between [-1,1]
            indicator /= float(hlen * tlen)

            current_Prices = data[stock].price
            notional = self.portfolio.positions[stock].amount * current_Prices
            transaction_price = indicator * self.capital_base * 10000

            if indicator >= 0 and notional < self.max_notional \
                    and self.days % self.rebalance_period == 0:
                if self.manager:
                    scale[stock] = abs(indicator * self.capital_base)
                    signals['buy'][stock] = data[stock]
                else:
                    self.order(stock, transaction_price)
                    self.logger.notice("[{}] {} shares of {} bought.".format(
                        self.datetime, transaction_price, stock))

            if indicator < 0 and notional > self.min_notional \
                    and self.days % self.rebalance_period == 0:
                if self.manager:
                    scale[stock] = abs(indicator * self.capital_base)
                    signals['sell'][stock] = data[stock]
                else:
                    self.order(stock, transaction_price)
                    self.logger.notice("[{}] {} shares of {} sold.".format(
                        self.datetime, abs(transaction_price), stock))

        self.manager.advise(scale=scale)
        return signals


@batch_transform
def calculate_theta(datapanel, sid, num):
    prices = datapanel['price'][sid]
    for i in range(len(prices)):
        if prices[i] is None:
            return None
    testX = [[prices[i] for i in range(j, j + 4)] for j in range(0, 60, 5)]
    avg = [np.average(testX[k]) for k in range(len(testX))]
    testY = [np.sign(prices[5 * i + 4] - avg[i]) for i in range(len(testX))]
    theta = hlsgdA(testX, testY, 0.01, randomIndex, num)
    priceh = prices[-4:]  # get historical data for the last four days
    return (theta, priceh)


# stochastic gradient descent using hinge loss function
def hlsgdA(X, Y, l, nextIndex, numberOfIterations):
    theta = np.zeros(len(X[0]))
    best = np.zeros(len(X[0]))
    e = 0
    omega = 1.0 / (2 * len(Y))
    while e < numberOfIterations:
        ita = 1.0 / (1 + e)
        for i in range(len(Y)):
            index = nextIndex(len(Y))
            k = np.dot(ita, (np.dot(l, np.append([0], [k for k in theta[1:]]))
                       - np.dot((sign(1 - Y[index] * np.dot(
                           theta, X[index])) * Y[index]), X[index])))
            theta -= k
            # A recency-weighted average of theta: an average that
            # exponentially decays the influence of older theta values
            best = (1 - omega) * best + omega * theta
        e += 1
    return best


# sign operations to identify mistakes
def sign(k):
    return 0 if k <= 0 else 1


def randomIndex(n):
    return random.randint(0, n - 1)
