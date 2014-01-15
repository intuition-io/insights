Algorithms
==========

API
---

```python
class MyAlgo(TradingFactory):
  '''
  Place for the trading strategy.

  The class provides the following useful attributes :
    - manager - Manager object specified on command line
    - portfolio - Portfolio informations
    - perf_tracker - Trading metrics
    - datetime - Current datetime
    - day - Day counter
    - logger
  '''
  def initialize(self, properties):
    '''
    This function runs once, before any trading event.
    '''
    # `properties` is a dictionnary storing parameters you set outside.
    self.short_window = properties.get('short_window', 15)
    self.long_window = properties.get('long_window', 30)

    # Intuition comes with battery included
    # Middlewares are trading tools. self.use() is sugar syntax that tells the
    # algorithm to call the provided function after each event
    if properties.get('save'):
        self.use(database.RethinkdbBackend(self.identity, True)
                 .save_portfolio)

  def warming(self, data):
    '''
    An other function ran once, after everything has been initialized, the
    very first time of trading
    '''
    # Fit a model before backtesting for example
    self.training_model = train_on_past_data()

  def event(self, data):
    '''
    Called for each event.
    If you can detect trading opportunities, this is where you
    place orders or fill the signals dictionnary : {'sid 1': price, 'sid 2': -price}
    The portfolio manager will use it compute the allocation : positive
    values are buy signals and vice versa.
    '''
    signals = {}

    for ticker in data:
        if great_prospect():
            # Currently, if you want to use weight-based strategy allocation,
            # you must provide the current sid price
            signals[ticker] = data[ticker].price
        if take_profit():
            signals[ticker] = -data[ticker].price

    return signals
```


Library
-------

* [Buy And Hold](https://github.com/hackliff/insights/blob/master/insights/algorithms/buyandhold.py)
> Buy every sids on the first day and until then

* [Dual Moving Average](https://github.com/hackliff/insights/blob/master/insights/algorithms/movingaverage.py)
# Buy when the short window crosses up the long window, and vice versa

* [Stochastic Gradient Method](https://github.com/hackliff/insights/blob/master/insights/algorithms/gradient.py)
