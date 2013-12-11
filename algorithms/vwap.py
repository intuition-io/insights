#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytz
import datetime

from intuition.zipline.algorithm import TradingFactory
from zipline.transforms import MovingVWAP


# https://www.quantopian.com/posts/updated-multi-sid-example-algorithm-1
class VolumeWeightAveragePrice(TradingFactory):
    '''
    '''
    def initialize(self, properties):
        # Common setup
        self.save = properties.get('save', 0)
        self.debug = properties.get('debug', 0)

        #self.buy_trigger = properties.get('buy_trigger', 0.995)
        #self.sell_trigger = properties.get('sell_trigger', 1.005)
        self.buy_trigger = 1 + (
            float(properties.get('buy_trigger', -5)) / 100)
        self.sell_trigger = 1 + (
            float(properties.get('sell_trigger', 5)) / 100)

        # Here we initialize each stock.  Note that we're not storing integers;
        # by calling sid(123) we're storing the Security object.
        self.vwap = {}
        self.price = {}

        # Setting our maximum position size, like previous example
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0

        # initializing the time variables we use for logging
        self.d = datetime.datetime(2005, 1, 10, 0, 0, 0, tzinfo=pytz.utc)

        self.add_transform(MovingVWAP, 'vwap', market_aware=True,
                           window_length=properties.get('window_length', 3))

    def event(self, data):
        signals = {}
        # Initializing the position as zero at the start of each frame
        notional = 0

        # This runs through each stock.  It computes
        # our position at the start of each frame.
        for stock in data:
            price = data[stock].price
            notional = notional + \
                self.portfolio.positions[stock].amount * price
            tradeday = data[stock].datetime

        # This runs through each stock again.  It finds the price and
        # calculates the volume-weighted average price.  If the price is moving
        # quickly, and we have not exceeded our position limits, it executes
        # the order and updates our position.
        for stock in data:
            vwap = data[stock].vwap
            price = data[stock].price

            if price < vwap * self.buy_trigger \
                    and notional > self.min_notional:
                signals[stock] = price
            elif price > vwap * self.sell_trigger \
                    and notional < self.max_notional:
                signals[stock] = -price

        # If this is the first trade of the day, it logs the notional.
        if (self.d + datetime.timedelta(days=1)) < tradeday:
            self.logger.debug(str(notional) + ' - notional start '
                              + tradeday.strftime('%m/%d/%y'))
            self.d = tradeday

        if not self.datetime.to_pydatetime() > self.portfolio.start_date:
            signals = {}

        return signals
