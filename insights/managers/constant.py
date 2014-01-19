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


from intuition.zipline.portfolio import PortfolioFactory


class Constant(PortfolioFactory):
    '''
    Buys and sells a constant defined amount
    '''
    def initialize(self, configuration):
        self.log.debug(configuration)

    def optimize(self, date, to_buy, to_sell, parameters):
        '''
        Buy sid * parameters['buy_amount'] * parameters['scale'][sid]
        Sell sid * parameters['sell_amount'] * parameters['scale'][sid]
        '''
        is_scaled = True if 'scale' in parameters else False
        allocations = {}

        # Process every stock the same way
        for s in to_buy:
            quantity = parameters.get('buy_amount', 100)
            if is_scaled:
                if s in parameters['scale']:
                    quantity *= parameters['scale'][s]
            # Allocate defined amount to buy
            allocations[s] = int(quantity)

        for s in to_sell:
            quantity = parameters.get(
                'sell_amount', self.portfolio.positions[s].amount)
            if is_scaled:
                if s in parameters['scale']:
                    quantity *= parameters['scale'][s]
            # Allocate defined amount to buy
            allocations[s] = -int(quantity)

        # Defaults values
        e_ret = 0
        e_risk = 1
        return allocations, e_ret, e_risk
