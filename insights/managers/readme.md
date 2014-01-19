Portfolio Managers
==================


API
---

```python
from portfolio import PortfolioFactory

class MyManager(PortfolioFactory):
    '''
    Manages portfolio during simulation, and stays aware of the situation
    through the update() method.

    User strategies call it with a dictionnnary of detected opportunities (i.e.
    buy or sell signals).  Then the optimize function computes assets
    allocation, returning a dictionnary of symbols with their weigths or amount
    to reallocate.

    {'buy': zipline.Positions}    __________________________      _____________
    signals                   --> |                         | -> |            |
                                  | trade_signals_handler() |    | optimize() |
    orders  {'google': 34}    <-- |_________________________| <- |____________|

    This is abstract class, inheretid class will eventally overwrite optmize()
    to expose their own asset allocation strategy.
    '''
    def initialize(configuration):
        '''
        This method runs only once and before any trade. Use it to initialize
        your strategy.
        '''

    def optimize(self, date, to_buy, to_sell, parameters):
        '''
        Specifies the portfolio's allocation strategy. Available:
        self.portfolio    : zipline portfolio object
        self.max_assets   : maximum assets the portfolio can have at a time
        self.max_weigths  : maximum weigth for an asset can have in the portfolio
        _____________________________________________
        Parameters
            date: datetime.timestamp
                Date signals were emitted
            to_buy: dict(...)
                Symbols with their strength to buy triggered by the strategy signals
            to_sell: dict(...)
                Symbols with their strength to sell triggered by the strategy signals
            parameters: dict(...)
                Custom user parameters
                An algo field in it stores data from the user-
                defined algorithm
        _____________________________________________
        Return:
            allocations: dict(...)
                Symbols with their -> weigths -> for buy: according the whole portfolio value   (must be floats)
                                              -> for sell: according total symbol position in portfolio
                                   -> amount: number of stocks to process (must be ints)
            e_ret: float
                Expected return
            e_risk: float
                Expected risk
        '''
```


Library
-------

Here is a list of the portfolio managers currently implemented, with a short
description and the parameters exposed (values are defaults)

* Global Minimum Variance
> Computes from data history a suitable compromise between risks and returns.
```python
parameters = {window: 40, only_full: True}
```

* OLMAR
> On-Line Portfolio Moving Average Reversion
```python
parameters = {eps: 1}
```

* Constant
> Buys and sells a constant defined amount
```python
parameters = {buy_amount: 100, sell_amount: 100, scale: {GOOG: 2, AAPL: 0.1}}
```

* Fair
> Dispatch equals weigths for buy signals and give up everything on sell ones
```python
parameters = {}
```

* Optimal Frontier
> Computes with R the efficient frontier and pick up the optimize point on it
```python
parameters = {per_sell: 1.0, max_weigths: 0.2, window: 50, refresh: 1, only_full: True}
```

* Black Litterman (work in progress)
> This algorithm performs a Black-Litterman portfolio construction. The
> framework is built on the classical mean-variance approach, but allows the
> investor to specify views about the over- or under- performance of various
> assets.  Uses ideas from the Global Minimum Variance Portfolio algorithm
> posted on Quantopian. Ideas also adopted from
> www.quantandfinancial.com/2013/08/portfolio-optimization-ii-black.html.
```python
parameters = {window: 255, refresh: 10, only_full: True}
```
