Middlewares
===========

API
---

```python
# This is work in progress
# Arguments names must be TradingFactory attributes
def debug_portfolio(portfolio, datetime):
    print datetime, portfolio
```

Then You can use it from the ``initialize()`` method.

```python
class BuyAndHold(TradingFactory):

    def initialize(self, properties):
        self.use(debug_portfolio)

```

Library
-------
