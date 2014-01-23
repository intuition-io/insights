Plugins
=======

API
---

Nothing special here, plugins are just useful code snippets for adding
features.


Middlewares
-----------

**Work in Progress**

Middlewares are special plugins. They expose a function which arguments are
intuition.zipline.TradingFactory attributes. Once this function registered at
initialization, *Intuition* will call it after each trading event (In the
futur, one will be able to specify more precisely when).

For example, the following code will print after each frame the current
portfolio.

```python
# Arguments names must be TradingFactory attributes or methods
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

* Database
> API(s) to manipulate currently [Rethinkdb][1] and [Influxdb][2] database
> systems. While *Influxdb* is still very experimental, you already can use
> Rethinkdb to store and access metrics while trading and stock quotes.
> Especially the [Database source][3] and the [telepathy plugin][4] use it
> under the hood.
>
> Check the [Official website][1] for installation or use a [docker image][5]
>
> As always here for third party softwares, configuration is stored as
> environment variables: `DB_HOST, DB_PORT[, DB_NAME, DB_USER, DB_PASSWORD]`.
> Alternately, the constructor lets you pass `host, port, db and table` keywords.
>
```python
from insights.plugins.database import RethinkdbBackend
from datetime import datetime

db = RethinkdbBackend(db='quotes')
data = self.db.quotes(['goog', 'aapl'],
                      start=datetime(2012, 01, 01),
                      end=datetime(2014, 01, 01),
                      select='close')
print data.head()
```
> You can also use it as a middleware
```python
from insights.plugins.database import RethinkdbBackend

class RandomStrategy(TradingFactory):
    def initialize(self, properties):
      self.use(RethinkdbBackend(self.identity, True).save_portfolio)
```

* Messaging
> Messaging skills for algorithms
> It uses redis to listen for incoming messages and publish informations
> The final goal is to provide algo <-> algo and user <-> algo communication
> abilities
```python
# Let's use it again as a middleware
# It will check for orders at each event
from insights.plugins.messaging import RedisProtocol

class RandomStrategy(TradingFactory):
    def initialize(self, properties):
      channel = 'chuck'
      self.use(RedisProtocol(channel).check)
```
> In another terminal
```console
$ # Connect to a running redis instance used by "intuition"
$ redis-cli -h 172.17.0.3
$ # Order 12 stocks of 'goog'
$ redis 172.17.0.3:6379> rpush "chuck" "{'goog': 12}"
```

* Mobile
> Push Android notifications using [Pushbullet][6] service (they plan to
> address iphones soon)
> You need to subscribe and download (free and free) the app on your androphone
> (but not necessarily as you can also send notifications to desktop computers).
> Then login, notice your device name and export in the environment your
> `PUSHBULLET_API_KEY`
```python
from insights.plugins.mobile import AndroidPush

# Initialize it with your device name
mobile = AndroidPush('HTC One S')
# Notify an order from an algorithm
mobile.push({'body': 'Hi, I am your personal trading bot'})

# The following functions works also as a middleware
mobile.notify({'goog': -27, 'aapl': 12})
```

* Mail
> Send emails using [Mailgun][7] API
> As for the others, export your `MAILGUN_API_KEY`
```python
from insights.plugins.mail import Mailgun

mail = Mailgun('Trading Bot', 'mydomain.com')

mail.send(['director@nsa.gouv', 'me@gmail.com'],
          subject='I hacked the market',
          body='bazinga')
```

* Utils
> Various useful snippets
```python
from insights.plugins.utils import debug_portfolio

class RandomStrategy(TradingFactory):
    def initialize(self, properties):
      self.use(debug_portfolio)
```

[1]: rethinkdb.com
[2]: influxdb.org
[3]: https://github.com/hackliff/insights/blob/master/insights/sources/backtest/database.py
[4]: https://github.com/hackliff/intuition-plugins/tree/master/rest
[5]: https://index.docker.io/u/dockerfile/rethinkdb/
[6]: pushbullet.com
[7]: mailgun.com
