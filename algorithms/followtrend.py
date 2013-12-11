#
# Copyright 2013 Xavier Bruhiere
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


import numpy as np
import statsmodels.api as sm

from zipline.transforms import batch_transform

from intuition.zipline.algorithm import TradingFactory


@batch_transform
def ols_transform(data):
    regression = {}
    for sid in data.price:
        prices = data.price[sid].values
        x = np.arange(1, len(prices) + 1)
        #NOTE Dev stuff: Without statsmodels, no scipy and without those two
        #     libs, container is much more quick to build
        x = sm.add_constant(x, prepend=True)
        regression[sid] = sm.OLS(prices, x).fit().params
    return regression


# http://nbviewer.ipython.org/4631031
class FollowTrend(TradingFactory):

    def initialize(self, properties):

        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)

        self.buy_trigger = properties.get('buy_trigger', .4)
        self.sell_trigger = properties.get('sell_trigger', -self.buy_trigger)
        self.buy_leverage = properties.get('buy_leverage', 50)
        self.sell_leverage = properties.get('sell_leverage', self.buy_leverage)

        self.ols_transform = ols_transform(
            refresh_period=properties.get('refresh_period', 1),
            window_length=properties.get('window_length', 50),
            fields='price')
        self.inter = 0
        self.slope = 0

    def event(self, data):
        self.buy = self.sell = False

        coeffs = self.ols_transform.handle_data(data)

        if coeffs is None:
            self.record(slope=self.slope,
                        buy=self.buy,
                        sell=self.sell)
            return

        for sid in data:
            self.inter, self.slope = coeffs[sid]

            if self.slope >= self.buy_trigger:
                self.order(sid, self.slope * self.buy_leverage)
                self.buy = True
            if self.slope <= -self.sell_trigger:
                self.order(sid, self.slope * self.sell_leverage)
                self.sell = True

        self.record(slope=self.slope,
                    buy=self.buy,
                    sell=self.sell)

        return {}
