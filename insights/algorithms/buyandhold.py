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


from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database
#import insights.plugins.messaging as msg
#from insights.plugins.utils import debug_portfolio


#TODO Should handle in parameter all of the set_*
class BuyAndHold(TradingFactory):
    '''
    Simpliest algorithm ever, just buy every stocks at the first frame
    '''
    def initialize(self, properties):
        #self.use(msg.RedisProtocol().check)
        self.save = properties.get('save', False)
        if self.save:
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

    def event(self, data):
        signals = {}

        if self.day == 2:
            ''' -----------------------------------------------    Scan   --'''
            for ticker in data:
                signals[ticker] = data[ticker].price

        ''' ---------------------------------------------------   Orders  --'''
        return signals
