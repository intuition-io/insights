from zipline.transforms import MovingAverage
import zipline.finance.commission as commission

from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database
import insights.plugins.mobile as mobile
import insights.plugins.messaging as msg


# https://www.quantopian.com/posts/this-is-amazing
class Momentum(TradingFactory):
    #FIXME Too much transactions, can't handle it on wide universe

    def initialize(self, properties):
        if properties.get('interactive'):
            self.use(msg.RedisProtocol(self.identity).check)
        device = properties.get('notify')
        if device:
            self.use(mobile.AndroidPush(device).notify)
        if properties.get('save'):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        self.max_notional = 2000.1
        self.min_notional = -2000.0

        self.max_weight = properties.get('max_weight', 0.2)
        self.max_exposure = properties.get('max_exposure', self.max_weight)

        self.add_transform(MovingAverage, 'mavg', ['price'],
                           window_length=properties.get('window', 3))

        self.set_commission(commission.PerTrade(
            cost=properties.get('commission', 2.5)))

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        for ticker in data:
            sma = data[ticker].mavg.price
            price = data[ticker].price
            cash = self.portfolio.cash
            notional = self.portfolio.positions[ticker].amount * price
            capital_used = self.portfolio.capital_used

            if sma > price and \
                    notional > -self.max_exposure * (capital_used + cash):
                signals['sell'][ticker] = data[ticker]
            elif sma < price and \
                    notional < self.max_weight * (capital_used + cash):
                signals['buy'][ticker] = data[ticker]

        return signals
