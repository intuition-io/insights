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

Here is a list of the algorithms currently implemented, with a short
description and the configuration exposed (values are defaults)

Most of them take also boolean parameters 'save' (portfolio metrics storage in
database), 'interactive' (manual commands through redis), 'notify' (andorid
notifications with [Push Bullet](pushbullet.com)) and 'commission' (the
transaction cost).

* Buy And Hold
> Buy every sids on the given day, regularly or always (start_day = -1), and
> until the end
```python
properties = {start_day: 2, rate: -1}
```

* Stochastic Gradient Method
> Randomly chooses training data, gradually decrease the learning rate, and
> penalize data points which deviate significantly from what's predicted. Here
> We used an average SGD method that is tested to outperform if we simply pick
> the last predictor value trained after certain iterations.
```python
properties = {refresh: 1, window: 60, gradient_iterations: 5}
```

* Regular Rebalance
> Reconsidere the portfolio allocation every <refresh> periods,
> providing to the portfolio strategy <window_length> days of quote data.
```python
properties = {refresh: 10, window: 40}
```

* Standard Deviation based (Always loose, there's something wrong !)
> Open Long Position if current price is larger than the 9 day volume weighted
> average plus 60% of the standard deviation Then positions are monitored with
> takeprofit and stoploss limits.  Plus, if we loose more than plug *
> starting_cash, we sell and stop trading.
```python
properties = {stddev: 9, vwap_window: 5, plug: 0.7}
```

* Auto adjusting stop loss
> The goal behind this algorithm was to invest in a broad range of stocks,
> eliminate the ones that aren't doing well, and "double down" on the ones that
> are.  The stop loss price is set as a function of the rate of return, and
> trails the current price so as to lock in a profit in the event that the
> price of a particular security starts dropping
```python
properties = {}
```

* Volume weight average price
> For each frame, it finds the price and calculates the volume-weighted average
> price.  If the price is moving quickly, and we have not exceeded our position
> limits, it executes the order and updates our position.
```python
properties = {window: 3, buy_trigger: -5, sell_trigger: 5}
```

* Momentum
> Buy when price > moving average and vice versa, but only if the stock
> notional is between max_weigth and max_expose
```python
properties = {window: 3, max_weight: 0.2, max_exposure: max_weight}
```

* Dual Moving Average
> Buys once its short moving average crosses its long moving average
> (indicating upwards momentum) and sells its shares once the averages cross
> again (indicating downwards momentum).
```python
properties = {long_window: 30, ma_rate: 0.5, short_window: ma_rate * long_window, threshold: 0}
```
