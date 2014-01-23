Data Sources
============


API
---

```python
from intuition.zipline.data_source import DataFactory

log = logbook.Logger('intuition.source.backtest|live.name')

class MySource(DataFactory):
  '''
  Data sources yield events, processed by the algorithms, from a data descriptor
  providing dates, trading universe (i.e. tickers, market, random, ...) and
  custom parameters.

  The class provides the following attributes :
    - self.sids - list of strings representing simulated internal sids
                  It can be an explicit list of symbols, or a universe like nyse,20
                  (that will pick up 20 random symbols from nyse exchange)
    - self.index - pandas.tseries.index.DatetimeIndex
    - self.start - self.index[0]
    - self.end - self.index[-1]
  '''

  def initialize(data_descriptor, **kwargs):
    '''
    Like with the other modules, ran once before trading. The data_descriptor
    holds dates index, the market universe as given by '--universe' and
    additional parameters the user wrote int the configuration under the 'data'
    key.
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
    return pd.DataFrame()

  @property
  def mapping(self):
    '''
    Sanitize your data input with correct fields and filters. You need at least
    to expose the following fields with their related types.
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

* Backtest.database
> Loads data from a [Rethinkdb][1] database.
> The universe can be any of yahoo-like symbols list, or `random[,n]` where n
> is an optional number of stocks.
> The `intuition-db` script is provided to feed some data to *Intuition*
```python
data_descriptor = {'database': 'quotes'}
```

* Backtest.quandl
> Fetch datasets from [Quandl][2].
> You can use yahoo-like symbols or market shortcuts (currently supported :
> cac40, nasdaq)

* Backtest.yahoo
> Fetch data from Yahoo finance.
> You can use yahoo-like symbols or market shortcuts (currently supported :
> cac40, nasdaq, nyse)
> YahooPrices allocates a dataframe of sids close prices, while
> YahooOHLC uses a panel of sid dataframes (with ohlc data)

* Backtest.csv
> Reads data from `.csv` files. For now, each file must be named {{ sid }}.csv
> (one sid data per file) and expose an header with at least a `Date` column
> for index. Those files must be located in ~/.intuition/data.
> The `--universe` option only understands comma separated list of csv files

* Live.forex
> Fetch real-time frex data from [TrueFX][3]
> You must subscribe to the service and export your logins like :
> `username:password`. Then you can provide a comma separated list of pairs or
> a market shortcut (forex[,n] where n is an optinal number of random pairs to
> trade)

* Live.equities
> Stream data from google finance.
> You can use the same universe options as backtest.yahoo

[1]: rethinkdb.com
[2]: quandl.com
[3]: http://www.truefx.com/
