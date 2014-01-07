# encoding: utf-8
#
# Copyright 2013 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import random
import numpy as np

from zipline.transforms import batch_transform

from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database


# https://www.quantopian.com/posts/\
# second-attempt-at-ml-stochastic-gradient-descent-\
# method-using-hinge-loss-function
class StochasticGradientDescent(TradingFactory):
    '''
    '''
    def initialize(self, properties):
        if properties.get('save', 0):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        self.rebalance_period = properties.get('rebalance_period', 5)

        self.bet_amount = self.capital_base
        self.max_notional = self.capital_base + 0.1
        self.min_notional = -self.capital_base
        self.gradient_iterations = properties.get('gradient_iterations', 5)
        self.calculate_theta = calculate_theta(
            refresh_period=properties.get('refresh_period', 1),
            window_length=properties.get('window_length', 60))

    def event(self, data):
        ''' ---------------------------------------------------    Init   --'''
        signals = {}

        for stock in data:
            thetaAndPrices = self.calculate_theta.handle_data(
                data, stock, self.gradient_iterations)
            if thetaAndPrices is None:
                continue

            theta, historicalPrices = thetaAndPrices

            # Indicator is a new manager !
            indicator = np.dot(theta, historicalPrices)
            # normalize
            hlen = sum([k * k for k in historicalPrices])
            tlen = sum([j * j for j in theta])
            # Makes the indicator lies between [-1,1]
            indicator /= float(hlen * tlen)

            current_Prices = data[stock].price
            notional = self.portfolio.positions[stock].amount * current_Prices

            if indicator >= 0 and notional < self.max_notional \
                    and self.day % self.rebalance_period == 0:
                #TODO indicator should be used to pondrate
                #     However it is much too small
                signals[stock] = current_Prices
                #self.order(stock, indicator * self.capital_base * 10000)
                #self.logger.notice("[%s] %f shares of %s bought." % \
                #(self.datetime, self.capital_base * indicator * 10000, stock))

            if indicator < 0 and notional > self.min_notional \
                    and self.day % self.rebalance_period == 0:
                signals[stock] = - current_Prices
                #self.order(stock, indicator * self.capital_base * 10000)
                #self.logger.notice("[%s] %f shares of %s sold." % \
                #(self.datetime, self.capital_base * indicator * 10000, stock))

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
    if k <= 0:
        return 0
    else:
        return 1


def randomIndex(n):
    return random.randint(0, n - 1)
