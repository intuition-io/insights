# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Manager utilities
  -----------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

import numpy as np
import scipy.optimize


def simplex_projection(v, b=1):
    """Projection vectors to the simplex domain

    Implemented according to the paper: Efficient projections onto the
    l1-ball for learning in high dimensions, John Duchi, et al. ICML 2008.
    Implementation Time: 2011 June 17 by Bin@libin AT pmail.ntu.edu.sg
    Optimization Problem: min_{w}\| w - v \|_{2}^{2}
    s.t. sum_{i=1}^{m}=z, w_{i}\geq 0

    Input: A vector v \in R^{m}, and a scalar z > 0 (default=1)
    Output: Projection vector w

    :Example:
    >>> proj = simplex_projection([.4 ,.3, -.4, .5])
    >>> print(proj)
    np.array([ 0.33333333, 0.23333333, 0. , 0.43333333])
    >>> print(proj.sum())
    1.0

    Original matlab implementation: John Duchi (jduchi@cs.berkeley.edu)
    Python-port: Copyright 2013 by Thomas Wiecki (thomas.wiecki@gmail.com).
    """

    v = np.asarray(v)
    p = len(v)

    # Sort v into u in descending order
    v = (v > 0) * v
    u = np.sort(v)[::-1]
    sv = np.cumsum(u)

    rho = np.where(u > (sv - b) / np.arange(1, p + 1))[0][-1]
    theta = np.max([0, (sv[rho] - b) / (rho + 1)])
    w = (v - theta)
    w[w < 0] = 0
    return w


# Weights - array of asset weights (derived from market capitalizations)
# Expreturns - expected returns based on historical data
# Covars - covariance matrix of asset returns based on historical data
def assets_meanvar(daily_returns, trading_days_per_year=255):
    # Calculate expected returns
    expreturns = np.array([])
    (rows, cols) = daily_returns.shape
    for r in range(rows):
        expreturns = np.append(expreturns, np.mean(daily_returns[r]))

    # Compute covariance matrix
    covars = np.cov(daily_returns)
    # Annualize expected returns and covariances
    expreturns = (1 + expreturns) ** trading_days_per_year - 1
    covars = covars * trading_days_per_year

    return expreturns, covars


# Solve for optimal portfolio weights
def solve_weights(R, C, rf):
    n = len(R)
    # Start optimization with equal weights
    W = np.ones([n]) / n
    # Bounds for decision variables
    b_ = [(0.1, 1) for i in range(n)]
    # Constraints - weights must sum to 1
    c_ = ({'type': 'eq', 'fun': lambda W: sum(W) - 1.})
    # 'target' return is the expected return on the market portfolio
    optimized = scipy.optimize.minimize(
        fitness, W, (
            R, C, sum(R * W)), method='SLSQP', constraints=c_, bounds=b_)
    if not optimized.success:
        #NOTE Or np.zeros ?
        return np.ones([n]) / n
        #raise BaseException(optimized.message)
    return optimized.x


# Compute the expected return of the portfolio.
def compute_mean(W, R):
    return sum(R * W)


# Compute the variance of the portfolio.
def compute_var(W, C):
    return np.dot(np.dot(W, C), W)


def fitness(W, R, C, r):
    # For given level of return r, find weights which minimizes portfolio
    # variance.
    mean_1, var = compute_mean(W, R), compute_var(W, C)
    # Penalty for not meeting stated portfolio return effectively serves as
    # optimization constraint
    # Here, r is the 'target' return
    penalty = 0.1 * abs(mean_1 - r)
    return var + penalty
