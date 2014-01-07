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


import os
import sys
import copy
import logbook

import rethinkdb as rdb
from influxdb import client as influxdb


# We will use these settings later in the code to
# connect to the RethinkDB server.
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 28015),
    'db': os.getenv('DB_NAME', 'intuition'),
    'user': os.getenv('DB_USER', 'quant'),
    'password': os.getenv('DB_PASSWORD', 'ity')
}


log = logbook.Logger('intuition.plugins.database')


def _to_dict(portfolio):
    json_pf = portfolio.__dict__
    if json_pf['positions']:
        for sid, infos in portfolio.positions.iteritems():
            json_pf['positions'][sid] = infos.__dict__
    return json_pf


#TODO Store TradingAlgo.recorded_vars
class RethinkdbBackend():
    '''
    Adds RethinkDB database backend to the portfolio
    '''
    def __init__(self, name, reset=False):
        try:
            self.session = self._connection()
        except rdb.RqlDriverError, error:
            sys.exit(error)
        self.table = name

        # Prepare the database
        if DB_CONFIG['db'] not in rdb.db_list().run(self.session):
            rdb.db_create(DB_CONFIG['db'])
            self.session = self._connection()
        if reset:
            self._reset_data(self.table)

    def _reset_data(self, table):
        if table in rdb.table_list().run(self.session):
            result = rdb.table_drop(table).run(self.session)
            assert result['dropped'] == 1

        result = rdb.table_create(table).run(self.session)
        result = rdb.table(table).index_create('date').run(self.session)
        return result.get('created', 0) == 1

    def _connection(self):
        return rdb.connect(host=DB_CONFIG['host'],
                           port=DB_CONFIG['port'],
                           db=DB_CONFIG['db'])

    def save_portfolio(self, datetime, portfolio, perf_tracker):
        '''
        Store in Rethinkdb a zipline.Portfolio object
        '''
        if perf_tracker.progress != 0.0:
            log.info('Saving portfolio in database')
            result = rdb.table(self.table).insert(
                {'date': datetime,
                 'cmr': perf_tracker.cumulative_risk_metrics.to_dict(),
                 'portfolio': _to_dict(
                     copy.deepcopy(portfolio))}).run(self.session)
            log.debug(result)

    def save_metrics(self, datetime, perf_tracker):
        '''
        Stores in database zipline.perf_tracker.cumulative_risk_metrics
        '''
        if perf_tracker.progress != 0.0:
            log.info('Saving cummulative metrics in database')
            result = rdb.table(self.table).insert(
                {'date': datetime,
                 'cmr': perf_tracker.cumulative_risk_metrics.to_dict()
                 }).run(self.session)
            log.debug(result)

    def load_portfolio(self, name):
        '''
        Build zipline.Portfolio object from <name> stored in database
        '''
        pass

    def __del__(self):
        self.session.close()


class InfluxdbBackend():
    '''
    Adds InfluxDB database backend to the portfolio
    '''
    def __init__(self, name):
        self.name = name
        self.session = self._connection()

    def _connection(self):
        #TODO No error raised if it fails, check it yourself
        return influxdb.InfluxDBClient(
            DB_CONFIG['host'], DB_CONFIG['port'],
            DB_CONFIG['user'], DB_CONFIG['password'], DB_CONFIG['db'])

    def save_portfolio(self, datetime, portfolio):
        '''
        Store in Rethinkdb a zipline.Portfolio object
        '''
        log.info('Saving portfolio in database')
        pf = _to_dict(copy.deepcopy(portfolio))
        pf.pop('positions')
        data = [{
            "name": self.name,
            "time": datetime.strftime("%Y-%m-%d %H:%M"),
            "columns": pf.keys(),
            "points": [pf.values()]}]
        # Timestamp type is not json serializable
        data[0]['points'][0][-1] = pf['start_date'].__str__()

        self.session.write_points(data)
