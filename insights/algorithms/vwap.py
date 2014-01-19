from zipline.transforms import MovingVWAP
import zipline.finance.commission as commission

from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database
import insights.plugins.mobile as mobile
import insights.plugins.messaging as msg


# https://www.quantopian.com/posts/updated-multi-sid-example-algorithm-1
class VolumeWeightAveragePrice(TradingFactory):

    def initialize(self, properties):
        # Common setup
        if properties.get('interactive'):
            self.use(msg.RedisProtocol(self.identity).check)
        device = properties.get('notify')
        if device:
            self.use(mobile.AndroidPush(device).notify)
        if properties.get('save'):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        self.buy_trigger = 1 + (
            float(properties.get('buy_trigger', -5)) / 100)
        self.sell_trigger = 1 + (
            float(properties.get('sell_trigger', 5)) / 100)

        # Setting our maximum position size, like previous example
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0

        self.add_transform(MovingVWAP, 'vwap', market_aware=True,
                           window_length=properties.get('window_length', 3))

        self.set_commission(commission.PerTrade(
            cost=properties.get('commission', 2.5)))

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        # Initializing the position as zero at the start of each frame
        notional = 0
        # This runs through each stock.  It computes
        # our position at the start of each frame.
        for stock in data:
            price = data[stock].price
            notional = notional + \
                self.portfolio.positions[stock].amount * price

        # This runs through each stock again.  It finds the price and
        # calculates the volume-weighted average price.  If the price is moving
        # quickly, and we have not exceeded our position limits, it executes
        # the order and updates our position.
        for stock in data:
            vwap = data[stock].vwap
            price = data[stock].price

            if price < vwap * self.buy_trigger \
                    and notional > self.min_notional:
                signals['buy'][stock] = data[stock]
            elif price > vwap * self.sell_trigger \
                    and notional < self.max_notional:
                signals['sell'][stock] = data[stock]

        return signals
