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


import zipline.finance.commission as commission

from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database
import insights.plugins.mobile as mobile
import insights.plugins.messaging as msg


class BuyAndHold(TradingFactory):
    '''
    Buy every sids on the given day, regularly or always (start_day = -1), and
    until the end
    '''
    def initialize(self, properties):
        # Punctual buy signals, with -1 for always, 0 never
        self.start_day = properties.get('start_day', 2)
        # regularly buy signals
        self.rate = properties.get('rate', -1)

        if properties.get('interactive'):
            self.use(msg.RedisProtocol(self.identity).check)
        device = properties.get('notify')
        if device:
            self.use(mobile.AndroidPush(device).notify)
        if properties.get('save'):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        self.set_commission(commission.PerTrade(
            cost=properties.get('commission', 2.5)))

    def _check_rate(self):
        return (self.rate > 0) and (self.days % self.rate == 0)

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}

        # One shot or always buying or regularly
        if self.days == self.start_day \
                or self.start_day < 0 \
                or self._check_rate():
            # Only cares about buying everything
            signals['buy'] = data

        return signals
