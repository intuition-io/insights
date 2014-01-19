from zipline.transforms import MovingVWAP, MovingStandardDev
import zipline.finance.commission as commission

from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database
import insights.plugins.mobile as mobile
import insights.plugins.messaging as msg


#TODO Now zipline offers orders methods with limit and stop loss
class StddevBased(TradingFactory):

    def initialize(self, properties):
        if properties.get('save'):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)
        device = properties.get('notify')
        if device:
            self.use(mobile.AndroidPush(device).notify)
        if properties.get('interactive'):
            self.use(msg.RedisProtocol(self.identity).check)

        # Variable to hold opening price of long trades
        self.long_open_price = 0
        # Variable to hold stoploss price of long trades
        self.long_stoploss = 0
        # Variable to hold takeprofit price of long trades
        self.long_takeprofit = 0
        # Allow only 1 long position to be open at a time
        self.long_open = False

        # Initiate Tally of successes and fails

        # Initialised at 0.0000000001 to avoid dividing by 0 in
        # winning_percentage calculation (meaning that reporting will get more
        # accurate as more trades are made, but may start off looking strange)
        self.successes = 0.0000000001
        self.fails = 0.0000000001

        # Variable for emergency plug pulling (if you lose more than 30%
        # starting capital, trading ability will be turned off... tut tut tut
        # :shakes head dissapprovingly:)
        self.plug_pulled = False
        self.plug_trigger = properties.get('plug', 0.7)

        self.add_transform(MovingStandardDev,
                           'stddev',
                           window_length=properties.get('stddev', 9))
        self.add_transform(MovingVWAP,
                           'vwap',
                           window_length=properties.get('vwap_window', 5))

        self.set_commission(commission.PerTrade(
            cost=properties.get('commission', 2.5)))

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        # Reporting Variables
        total_trades = self.successes + self.fails
        winning_percentage = self.successes / total_trades * 100

        # Data Variables
        for stock in data:
            price = data[stock].price
            vwap_5_day = data[stock].vwap
            standard_deviation = data[stock].stddev
            equity = self.portfolio.cash + self.portfolio.positions_value
            if not standard_deviation:
                continue

            # Open Long Position if current price is larger than the 9 day
            # volume weighted average plus 60% of the standard deviation
            # (meaning the price has broken it's range to the up-side by 10%
            # more than the range value)
            if price > vwap_5_day + (standard_deviation * 0.6) \
                    and self.long_open is False:
                signals['buy'][stock] = data[stock]
                self.long_open = True
                self.long_open_price = price
                self.long_stoploss = (
                    self.long_open_price - standard_deviation * 0.6)
                self.long_takeprofit = (
                    self.long_open_price + standard_deviation * 0.5)

            # Close Long Position if takeprofit value hit
            # Note that less volatile stocks can end up hitting takeprofit at a
            # small loss
            if price >= self.long_takeprofit and self.long_open is True:
                signals['sell'][stock] = data[stock]
                self.long_open = False
                self.long_takeprofit = 0
                self.successes = self.successes + 1

                self.logger.info('{} Long Position Closed by Takeprofit at ${}'
                                 .format(stock, price))
                self.logger.info('Total Equity now at ${}'.format(equity))
                self.logger.info('So far you have had {} successful trades and\
                    {} failed trades'.format(self.successes, self.fails))
                self.logger.info('That leaves you with a winning percentage of\
                    {} percent'.format(winning_percentage))

            # Close Long Position if stoploss value hit
            if price <= self.long_stoploss and self.long_open is True:
                signals['sell'][stock] = data[stock]
                self.long_open = False
                self.long_stoploss = 0
                self.fails = self.fails + 1
                self.logger.info('{} long Position Closed by Stoploss at ${}'
                                 .format(stock, price))
                self.logger.info('Total Equity now at ${}'.format(equity))
                self.logger.info('So far you have had {} successful trades and\
                  {} failed trades'.format(self.successes, self.fails))
                self.logger.info('That leaves you with a winning percentage of\
                  {} percent'.format(winning_percentage))

            # Pull Plug?
            if equity < self.portfolio.starting_cash * self.plug_trigger:
                self.plug_pulled = True
                self.logger.info("Ouch! We've pulled the plug...")

            if self.plug_pulled is True and self.long_open is True:
                signals['sell'][stock] = data[stock]
                self.long_open = False
                self.long_stoploss = 0

        return signals
