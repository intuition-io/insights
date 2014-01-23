Insights
========

[![Latest Version](https://pypip.in/v/insights/badge.png)](https://pypi.python.org/pypi/insights/)
[![Build Status](https://travis-ci.org/hackliff/insights.png?branch=master)](https://travis-ci.org/hackliff/insights)
[![Coverage Status](https://coveralls.io/repos/hackliff/insights/badge.png)](https://coveralls.io/r/hackliff/insights)
[![Code Health](https://landscape.io/github/hackliff/insights/master/landscape.png)](https://landscape.io/github/hackliff/insights/master)
[![Requirements Status](https://requires.io/github/hackliff/insights/requirements.png?branch=master)](https://requires.io/github/hackliff/insights/requirements/?branch=master)
[![License](https://pypip.in/license/insights/badge.png)](https://pypi.python.org/pypi/insights/)

> Plug-and-play building blocks for modern quants

Quantitative algorithms, portfolio managers data sources, contexts and
middlewares for [Intuition][3]. Once provided to the configuration, those
modules, or the ones you create, are automatically used.

[Development Board][1]


Installation
------------

* One-liner

```console
$ wget -qO- http://bit.ly/1anxGhf | sudo FULL_INTUITION=true bash
```

* Step by step

```console
$ sudo apt-get install r-base
$ # Install R libraries
$ wget -qO- http://bit.ly/L39jeY | R --no-save
$ (sudo) pip install intuition

$ (sudo) pip install insights
```

Or if you plan to hack on it

```console
$ git clone https://github.com/hackliff/insights.git && cd insights
$ (sudo) pip install -r requirements.txt
$ # Install R code
$ cp -r R/ ~/.intuition
$ export PYTHONPATH=$PYTHONPATH:$PWD
```

Either way, you can use in your *intuition* configuration something like

```yaml
algorithm:
  # Set here parameters you want to be accessible in the init function
  notify: Nexus 5
  long_window: 32
manager:
  # And here those you will find under the $parameters dict in optimize()
  max_weight: 0.3
modules:
  manager: insights.managers.fair.Fair
  algorithm: insights.algorithms.gradient.StochasticGradientDescent
  data: insights.sources.live.EquitiesLiveSource
```

Check out readmes and source codes to learn what is available and the
parameters exposed. Documentation is on its way !


Code your own modules
---------------------

* [Algorithm API](https://github.com/hackliff/insights/blob/master/insights/algorithms/readme.md)
* [Portfolio API](https://github.com/hackliff/insights/blob/master/insights/managers/readme.md)
* [Data API](https://github.com/hackliff/insights/blob/master/insights/sources/readme.md)
* [Contexts](https://github.com/hackliff/insights/blob/master/insights/contexts/readme.md)
* [Middlewares](https://github.com/hackliff/insights/blob/master/insights/contexts/readme.md)

Here are some examples to get you started. To make your work available, just
feed the [Intuition][3] configuration (like above) a path it can find in the
environment variable `$PYTHONPATH`.

Everything is done to make writing modules easy, fun and efficient. So your
feedback, advices and contributions are happily welcome

* First, a classic buy and hold strategy, with a plugin which stores metrics in
[rethinkdb](www.rethinkdb.com):

```python
from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database

class BuyAndHold(TradingFactory):
    '''
    Simpliest algorithm ever, just buy every stocks at the first frame
    '''
    def initialize(self, properties):

        if properties.get('save'):
            self.use(database.RethinkdbBackend(self.identity, reset=True)
                     .save_portfolio)

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        if self.day == 2:
            for ticker in data:
                signals['buy'][ticker] = data[ticker]

        return signals
```

* Here is the Fair manager example, which allocates the same weight in the
  portfolio to all of your assets:

```python
from intuition.zipline.portfolio import PortfolioFactory

class Fair(PortfolioFactory):
    '''
    Dispatch equals weigths for buy signals and give up everything on sell ones
    '''
    def optimize(self, date, to_buy, to_sell, parameters):
        # The algorithm fills 'to_buy' and 'to_sell' dicts by detecting
        # buy and sell signals
        # This dictionnary holds portfolio manager recommendations
        allocations = {}

        if to_buy:
            # Split the portfolio in equal parts for each stock to buy
            fraction = round(1.0 / float(len(to_buy)), 2)
            for s in to_buy:
                allocations[s] = fraction

        for s in to_sell:
            # Simply sells every stocks
            allocations[s] = - self.portfolio.positions[s].amount

        expected_return = 0
        expected_risk = 1
        return allocations, expected_return, expected_risk
```

* Now a source for backtests taking advantage of the awesome [Quandl][2] project.

```python
from intuition.zipline.data_source import DataFactory
from intuition.data.quandl import DataQuandl

class QuandlSource(DataFactory):
    '''
    Fetchs data from quandl.com
    '''
    def get_data(self):
        return DataQuandl().fetch(self.sids,
                          start_date=self.start,
                          end_date=self.end,
                          returns='pandas')

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'Close'),
            'volume': (int, 'Volume'),
            'open': (int, 'Open'),
            'low': (int, 'Low'),
            'high': (int, 'High'),
        }
```

Intuition-db
------------

A script is provided to help you fill the database (if you want to use the [Database source][4]).

```console
$ intuition-db -h
$ # Download data from 2012 to now for 20 random nasdaq stocks
$ intiution-db dl --start 2012-01-02 --universe nasdaq,20
```

[1]: https://trello.com/b/WvJDlynt/intuition
[2]: http://www.quandl.com/
[3]: https://github.com/hackliff/intuition
[4]: https://github.com/hackliff/insights/blob/master/insights/sources/backtest/database.py
