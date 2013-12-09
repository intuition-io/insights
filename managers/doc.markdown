Portfolio Managers
==================


API
---

```python
from portfolio import PortfolioFactory

class MyManager(PortfolioFactory):
    '''
    Manages portfolio during simulation, and stays aware of the situation
    through the update() method. It is configured through zmq message (manager
    field) or ~/.intuition/plugins.json file.

    User strategies call it with a dictionnnary of detected opportunities (i.e.
    buy or sell signals).  Then the optimize function computes assets
    allocation, returning a dictionnary of symbols with their weigths or amount
    to reallocate.
                                  __________________________      _____________
    signals {'google': 745.5} --> |                         | -> |            |
                                  | trade_signals_handler() |    | optimize() |
    orders  {'google': 34}    <-- |_________________________| <- |____________|

    In addition, portfolio objects can be saved in database and reloaded later,
    and user on-the-fly orders are catched and executed in remote mode. Finally
    portfolios are connected to the server broker and, if requested, send state
    messages to client.
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
