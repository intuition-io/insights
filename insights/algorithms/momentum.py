#
# Copyright 2014 Xavier Bruhiere
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


from zipline.transforms import MovingAverage

from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database


# https://www.quantopian.com/posts/this-is-amazing
class Momentum(TradingFactory):
    '''
    '''
    #FIXME Many transactions, so makes the algorithm explode when traded with
    #      many positions
    def initialize(self, properties):
        if properties.get('save', 0):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        self.max_notional = 100000.1
        self.min_notional = -100000.0

        self.add_transform(MovingAverage, 'mavg', ['price'],
                           window_length=properties.get('window_length', 3))

    def event(self, data):
        signals = {}
        notional = 0

        ''' ---------------------------------------------------    Scan   --'''
        for ticker in data:
            sma = data[ticker].mavg.price
            price = data[ticker].price
            cash = self.portfolio.cash
            notional = self.portfolio.positions[ticker].amount * price
            capital_used = self.portfolio.capital_used

            # notional stuff are portfolio strategies, implement a new one,
            # combinaison => parameters !
            if sma > price and notional > -0.2 * (capital_used + cash):
                signals[ticker] = price
            elif sma < price and notional < 0.2 * (capital_used + cash):
                signals[ticker] = - price

        return signals
