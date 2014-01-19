import zipline.finance.commission as commission

from intuition.zipline.algorithm import TradingFactory
import insights.transforms as transforms
import insights.plugins.database as database
import insights.plugins.mobile as mobile
import insights.plugins.messaging as msg


# https://www.quantopian.com/posts/global-minimum-variance-portfolio?c=1
class RegularRebalance(TradingFactory):
    '''
    Reconsidere the portfolio allocation every <refresh_period> periods,
    providing to the portfolio strategy <window_length> days of quote data.
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

        # Set Max and Min positions in security
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0

        self.set_commission(commission.PerTrade(
            cost=properties.get('commission', 2.5)))

        # This is the lookback window that the entire algorithm depends on
        self.refresh_period = properties.get('refresh', 10)
        self.returns_transform = transforms.get_past_returns(
            refresh_period=self.refresh_period,
            window_length=properties.get('window', 40),
            compute_only_full=True)

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        #get 20 days of prices for each security
        daily_returns = self.returns_transform.handle_data(data)

        #circuit breaker in case transform returns none
        #circuit breaker, only calculate every 10 days
        if (daily_returns is None) or \
                (self.days % self.refresh_period is not 0):
            return signals

        #reweight portfolio
        for sid in data:
            signals['buy'][sid] = data[sid]

        self.manager.advise(historical_returns=daily_returns)
        return signals
