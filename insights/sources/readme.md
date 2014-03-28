Data Sources
============


API
---

```python
class MyBacktestSource(object):
  '''
  Data sources yield events, processed by the algorithms, from a data descriptor
  providing dates, trading universe (i.e. tickers, market, random, ...) and
  custom parameters.
  '''

  def __init__(self, sids, properties):
    '''
    Intuition parsed user input and provides the sids it wants to trade on.
    Properties holds user configuration and specific market scheme.
    '''
    pass

  def get_data(self):
    '''
    Returns a pandas.DataFrame or pandas.Panel used as trading events.
    DataFactory can process the following schemes

          | goog | aapl                 | open | high | volume
    ------------------- ...  or   ---------------------------- ...
    14/03 | 34.5 | 345            14/03 | 34.3 | 37.8 | 120056
    15/03 | 34.9 | 344            15/03 | 36.3 | 36.9 | 103565

              or

      aapl / ..  /  ..  /  ..
     goog / ..  /  ..  /  ..
    -----| open | high | close ...
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
