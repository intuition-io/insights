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


from intuition.zipline.algorithm import TradingFactory


# https://www.quantopian.com/posts/moving-average-crossover
class MovingAverageCrossover(TradingFactory):
    '''
    '''
    def initialize(self, properties):
        self.debug = properties.get('debug', 0)
        self.save = properties.get('save', 0)

        self.fast = []
        self.slow = []
        self.medium = []
        self.breakoutFilter = 0

        self.passedMediumLong = False
        self.passedMediumShort = False

        self.holdingLongPosition = False
        self.holdingShortPosition = False

        self.entryPrice = 0.0

    def handle_data(self, data):
        ''' ---------------------------------------------------    Init   --'''
        if self.initialized:
            self.manager.update(
                self.portfolio,
                self.datetime.to_pydatetime(),
                self.perf_tracker.cumulative_risk_metrics.to_dict(),
                save=self.save,
                widgets=False)
        else:
            # Perf_tracker need at least a turn to have an index
            self.initialized = True

        signals = {}

        ''' ---------------------------------------------------    Scan   --'''
        for ticker in data:
            self.fast.append(data[ticker].price)
            self.slow.append(data[ticker].price)
            self.medium.append(data[ticker].price)

            fastMovingAverage = 0.0
            mediumMovingAverage = 0.0
            slowMovingAverage = 0.0

            if len(self.fast) > 30:
                self.fast.pop(0)
                fastMovingAverage = sum(self.fast) / len(self.fast)

            if len(self.medium) > 60 * 30:
                self.medium.pop(0)
                mediumMovingAverage = sum(self.medium) / len(self.medium)

            if len(self.slow) > 60 * 60:
                self.slow.pop(0)
                slowMovingAverage = sum(self.slow) / len(self.slow)

            if ((self.holdingLongPosition is False
                and self.holdingShortPosition is False)
                    and ((mediumMovingAverage > 0.0
                         and slowMovingAverage > 0.0)
                         and (mediumMovingAverage > slowMovingAverage))):
                self.passedMediumLong = True

            if ((self.holdingLongPosition is False
                and self.holdingShortPosition is False)
                and ((mediumMovingAverage > 0.0
                     and slowMovingAverage > 0.0)
                     and (mediumMovingAverage < slowMovingAverage))):
                self.passedMediumShort = True

            # Entry Strategies
            if (self.holdingLongPosition is False
                and self.holdingShortPosition is False
                and self.passedMediumLong is True
                and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                     and (fastMovingAverage > mediumMovingAverage))):

                if self.breakoutFilter > 5:
                    self.logger.info("ENTERING LONG POSITION")
                    signals[ticker] = data[ticker].price

                    self.holdingLongPosition = True
                    self.breakoutFilter = 0
                    self.entryPrice = data[ticker].price
                else:
                    self.breakoutFilter += 1

            if (self.holdingShortPosition is False
                and self.holdingLongPosition is False
                and self.passedMediumShort is True
                and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                     and (fastMovingAverage < mediumMovingAverage))):

                if self.breakoutFilter > 5:
                    self.logger.info("ENTERING SHORT POSITION")
                    #self.order(ticker, -100)
                    signals[ticker] = - data[ticker].price
                    self.holdingShortPosition = True
                    self.breakoutFilter = 0
                    self.entryPrice = data[ticker].price
                else:
                    self.breakoutFilter += 1

        # Exit Strategies
        if (self.holdingLongPosition is True
            and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                 and (fastMovingAverage < mediumMovingAverage))):

            if self.breakoutFilter > 5:
                signals[ticker] = - data[ticker].price
                self.holdingLongPosition = False
                self.breakoutFilter = 0
            else:
                self.breakoutFilter += 1

        if (self.holdingShortPosition is True
                and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                     and (fastMovingAverage > mediumMovingAverage))):
            if self.breakoutFilter > 5:
                signals[ticker] = data[ticker].price
                self.holdingShortPosition = False
                self.breakoutFilter = 0
            else:
                self.breakoutFilter += 1
        ''' ---------------------------------------------------   Orders  --'''
        self.process_signals(signals)

    def process_signals(self, signals):
        if not signals:
            return

        order_book = self.manager.trade_signals_handler(signals)

        for ticker in order_book:
            if self.debug:
                self.logger.notice('{} Ordering {} {} stocks'.format(
                    self.datetime, ticker, order_book[ticker]))
            self.order(ticker, order_book[ticker])
