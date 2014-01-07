Insights
========

[![Build Status](https://travis-ci.org/hackliff/insights.png?branch=develop)](https://travis-ci.org/hackliff/insights)
[![Coverage Status](https://coveralls.io/repos/hackliff/insights/badge.png)](https://coveralls.io/r/hackliff/insights)
[![Code Health](https://landscape.io/github/hackliff/insights/develop/landscape.png)](https://landscape.io/github/hackliff/insights/develop)

> Quantitative algorithms, portfolio managers data sources and contexts
> for [Intuition](https://github.com/hackliff/intuition)

* [Algorithm API](https://github.com/hackliff/insights/blob/develop/algorithms/readme.md)
* [Portfolio API](https://github.com/hackliff/insights/blob/develop/managers/readme.md)
* [Data API](https://github.com/hackliff/insights/blob/develop/sources/readme.md)
* [Contexts](https://github.com/hackliff/insights/blob/develop/contexts/readme.md)


Installation
------------

```
# apt-get install r-base
# pip install --use-mirrors numpy scipy patsy
# pip install -e git+https://github.com/hackliff/insights.git@develop#egg=insights-0.0.9
```


Getting started
---------------

Here is the Fair manager example, which allocates the same weight to all of your assets:

```python
from intuition.zipline.portfolio import PortfolioFactory

class Fair(PortfolioFactory):
    '''
    Dispatch equals weigths for buy signals and give up everything on sell ones
    '''
    def optimize(self, date, to_buy, to_sell, parameters):
        allocations = dict()
        if to_buy:
            fraction = round(1.0 / float(len(to_buy)), 2)
            for s in to_buy:
                allocations[s] = fraction
        for s in to_sell:
            allocations[s] = - self.portfolio.positions[s].amount

        expected_return = 0
        expected_risk = 1
        return allocations, expected_return, expected_risk
```

Here is a classic buy and hold strategy, with a plugin which stores metrics in
[rethinkdb](www.rethinkdb.com):

```python
from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database

class BuyAndHold(TradingFactory):
    '''
    Simpliest algorithm ever, just buy every stocks at the first frame
    '''
    def initialize(self, properties):

        self.save = properties.get('save', False)
        if self.save:
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

    def event(self, data):
        signals = {}

        if self.day == 2:
            for ticker in data:
                signals[ticker] = data[ticker].price

        return signals
```
