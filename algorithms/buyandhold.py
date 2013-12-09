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


#TODO Should handle in parameter all of the set_*
#TODO stop_trading or process_instruction are common methods
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

        self.loops = 0

    def handle_data(self, data):
        self.loops += 1
        signals = {}

        if self.debug:
            print('\n' + 79 * '=')
            print self.portfolio
            print(79 * '=' + '\n')

        ''' ---------------------------------------------------    Init   --'''
        if self.initialized:
            user_instruction = self.manager.update(
                self.portfolio,
                self.datetime,
                self.perf_tracker.cumulative_risk_metrics.to_dict(),
                save=self.save,
                widgets=False)
            self.process_instruction(user_instruction)
            #self.db.save_portfolio(self.datetime, self.portfolio)
            #self.db.save_metrics(
            #   self.datetime, self.perf_tracker.cumulative_risk_metrics)
        else:
            # Perf_tracker need at least a turn to have an index
            self.initialized = True
            #self.db = database.RethinkdbBackend(self.manager.name, True)

        if self.loops == 2:
            ''' -----------------------------------------------    Scan   --'''
            for ticker in data:
                signals[ticker] = data[ticker].price

        ''' ---------------------------------------------------   Orders  --'''
        if signals:
            orderBook = self.manager.trade_signals_handler(signals)
            for stock in orderBook:
                if self.debug:
                    self.logger.notice('{}: Ordering {} {} stocks'.format(
                        self.datetime, stock, orderBook[stock]))
                self.order(stock, orderBook[stock])

    def process_instruction(self, instruction):
        '''
        Process orders from instruction
        '''
        if instruction:
            self.logger.info('Processing user instruction')
            if (instruction['command'] == 'order') \
                    and ('amount' in instruction):
                self.logger.error('{}: Ordering {} {} stocks'.format(
                    self.datetime,
                    instruction['amount'],
                    instruction['asset']))

    #NOTE self.done flag could be used to avoid in zipline waist of computation
    #TODO Anyway should find a more elegant way
    def stop_trading(self):
        ''' Convenient method to stop calling user algorithm and just finish
        the simulation'''
        self.logger.info('Trader out of the market')
        #NOTE Selling every open positions ?
        # Saving the portfolio in database, eventually for reuse
        self.manager.save_portfolio(self.portfolio)

        # Closing generator
        self.date_sorted.close()
        #self.set_datetime(self.sim_params.last_close)
        self.done = True
