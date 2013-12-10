Data Sources
============


API
---

```python
from intuition.zipline.data_source import DataFactory

log = logbook.Logger('intuition.source.backtest|live.name')

class MySource(DataFactory):
  '''
  Data sources yield events processed by the algorithms, from a data descriptor
  providing dates and the trading universe (i.e. tickers, market, random, ...)

  The class provides the following attributes :
    - self.sids - list of strings representing simulated internal sids
                  It can be an explicit list of symbols, or a universe like nyse,20
                  (that will pick up 20 random symbols from nyse exchange)
    - self.index - pandas.tseries.index.DatetimeIndex
    - self.start - self.index[0]
    - self.end - self.index[-1]
  '''

  def get_data(self):
    '''
    Returns a pandas.DataFrame or pandas.Panel used as trading events.
    DataFactory can process the following schemes

          | goog | aapl              | open | high | volume
    -------------------   or   ----------------------------
    14/03 | 34.5 | 345         14/03 | 34.3 | 37.8 | 120056
    15/03 | 34.9 | 344         15/03 | 36.3 | 36.9 | 103565


      aapl / ..  /  ..  /  ..
     goog / ..  /  ..  /  ..
    -----| open | high | close
    14/03| ____ | ____ | _____
    15/03|      |      |
    '''

  @property
  def mapping(self):
    '''
    Sanitize your data input with correct fields and filters
    '''
    return {
        'dt': (lambda x: x, 'dt'),
        'sid': (lambda x: x, 'sid'),
        'price': (float, 'price'),
        'volume': (int, 'volume'),
    }
```


Library
-------
