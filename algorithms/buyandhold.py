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


from intuition.zipline.algorithm import TradingFactory
import intuition.modules.plugins.database as database


#TODO Should handle in parameter all of the set_*
class BuyAndHold(TradingFactory):
    '''
    Simpliest algorithm ever, just buy every stocks at the first frame
    '''
    def initialize(self, properties):
        #NOTE can't use it here, no self.manager yet. Issue ?
        #     Could configure every common parameters in Backtester engine
        #     and use setupe_strategie as an update
        #self.manager.setup_strategy({'commission_cost': self.commission.cost})
        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)

    def preamble(self, data):
        if self.save:
            self.db = database.RethinkdbBackend(self.manager.name, True)

    def event(self, data):
        signals = {}
        ''' ---------------------------------------------------    Init   --'''

        if self.day == 2:

            if self.save:
                self.db.save_portfolio(self.datetime, self.portfolio)
                self.db.save_metrics(
                    self.datetime, self.perf_tracker.cumulative_risk_metrics)
            ''' -----------------------------------------------    Scan   --'''
            for ticker in data:
                signals[ticker] = data[ticker].price

        ''' ---------------------------------------------------   Orders  --'''
        return signals
