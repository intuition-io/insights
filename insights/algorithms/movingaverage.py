from zipline.transforms import MovingAverage
import zipline.finance.commission as commission

from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database
import insights.plugins.mobile as mobile
import insights.plugins.messaging as msg


class DualMovingAverage(TradingFactory):
    '''
    Buys once its short moving average crosses its long moving average
    (indicating upwards momentum) and sells its shares once the averages cross
    again (indicating downwards momentum).
    '''
    def initialize(self, properties):
        if properties.get('interactive'):
            self.use(msg.RedisProtocol(self.identity).check)
        device = properties.get('notify')
        if device:
            self.use(mobile.AndroidPush(device).notify)
        if properties.get('save'):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        long_window = properties.get('long_window', 30)
        short_window = properties.get('short_window', None)
        if short_window is None:
            short_window = int(round(
                properties.get('ma_rate', 0.5) * float(long_window), 2))
        self.threshold = properties.get('threshold', 0)

        self.add_transform(MovingAverage, 'short_mavg', ['price'],
                           window_length=short_window)

        self.add_transform(MovingAverage, 'long_mavg', ['price'],
                           window_length=long_window)

        # To keep track of whether we invested in the stock or not
        self.invested = {}

        self.short_mavgs = []
        self.long_mavgs = []

        self.set_commission(commission.PerTrade(
            cost=properties.get('commission', 2.5)))

    def warming(self, data):
        for sid in data:
            self.invested[sid] = False

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        for ticker in data:

            short_mavg = data[ticker].short_mavg['price']
            long_mavg = data[ticker].long_mavg['price']

            if short_mavg - long_mavg > self.threshold \
                    and not self.invested[ticker]:
                signals['buy'][ticker] = data[ticker]
                self.invested[ticker] = True

            elif short_mavg - long_mavg < -self.threshold \
                    and self.invested[ticker]:
                signals['sell'][ticker] = data[ticker]
                self.invested[ticker] = False

        return signals
