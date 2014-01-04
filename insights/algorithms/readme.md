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
    properties is a dictionnary storing parameters you set outside.
    This function runs once, before any trading event.
    '''
    self.debug = properties.get('debug', False)
    self.save = properties.get('save', False)

  def warming(self, data):
    '''
    An other function ran once, after everything has been initialized, the
    very first time of trading
    '''
    # The database plugin lets you store portfolio and trading metrics
    if self.save:
      self.db = database.RethinkdbBackend(self.manager.name, True)

  def event(self, data):
    '''
    Called for each event.
    If you can detect trading opportunities, this is the opportunity to
    place orders or fill the signals dictionnary : {'sid 1': 1, 'sid 2': -1}
    The portfolio manager will use it compute the allocation : positive
    values are buy signals and vice versa.
    '''
    signals = {}

    if self.save:
      self.db.save_portfolio(self.datetime, self.portfolio)
      self.db.save_metrics(
        self.datetime, self.perf_tracker.cumulative_risk_metrics)

    for ticker in data:
      signals[ticker] = data[ticker].price

    return signals
```


Library
-------
