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


import os
import sys
import copy
import pytz
import random
import logbook
from clint.textui import progress
import pandas as pd

import rethinkdb as rdb
from influxdb import client as influxdb

import intuition.utils


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
    def __init__(self, **kwargs):
        host = kwargs.get('host', DB_CONFIG['host'])
        port = kwargs.get('port', DB_CONFIG['port'])
        db = kwargs.get('db', DB_CONFIG['db'])
        self.table = kwargs.get('table', None)

        try:
            self.session = self._connection(host, port, db)
        except rdb.RqlDriverError, error:
            sys.exit(error)

        # Prepare the database
        if db not in rdb.db_list().run(self.session):
            log.info('creating database {}'.format(db))
            rdb.db_create(db).run(self.session)
            self.session = self._connection(host, port, db)
        if kwargs.get('reset') and self.table:
            log.info('clearing table {}'.format(self.table))
            self._reset_data(self.table)

    def _reset_data(self, table):
        if table in rdb.table_list().run(self.session):
            result = rdb.table_drop(table).run(self.session)
            assert result['dropped'] == 1

        result = rdb.table_create(table).run(self.session)
        result = rdb.table(table).index_create('date').run(self.session)
        return result.get('created', 0) == 1

    def _connection(self, host, port, db):
        return rdb.connect(host=host, port=port, db=db)

    def save_portfolio(self, datetime, portfolio, perf_tracker):
        '''
        Store in Rethinkdb a zipline.Portfolio object
        '''
        if perf_tracker.progress != 0.0 and self.table:
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
        if perf_tracker.progress != 0.0 and self.table:
            log.info('Saving cummulative metrics in database')
            result = rdb.table(self.table).insert(
                {'date': datetime,
                 'cmr': perf_tracker.cumulative_risk_metrics.to_dict()
                 }).run(self.session)
            log.debug(result)

    def save_quotes(self, table, data, metadata={}, reset=False):
        if reset:
            self._reset_data(table)
        data.columns = map(lambda x: x.replace(' ', '_').lower(), data.columns)
        length = len(data)
        for dt, row in progress.bar(data.iterrows(), expected_size=length):
            record = row.to_dict()
            record.update({'date': dt})
            record.update(metadata)
            report = rdb.table(table).insert(record).run(self.session)
            assert not report['errors']

    def _load_quotes(self, sids, start, end, select):
        is_panel = (len(select) > 2)
        select.append('date')
        data = {}
        for table in sids:
            if table not in rdb.table_list().run(self.session):
                log.warning('{} not found in database, skipping'
                            .format(table))
                continue

            cursor_data = rdb.table(table)\
                .filter(lambda row: row['date'].during(
                        start, end))\
                .pluck(select)\
                .run(self.session)
            data[table] = {}

            for row in cursor_data:
                # tzinfo of the object is rethinkdb specific
                date = row.pop('date').astimezone(pytz.utc)
                #date = intuition.utils.normalize_date_format(
                    #row.pop('date')['epoch_time'])
                data[table][date] = row if is_panel else row[select[0]]

        if is_panel:
            data = {k: v for k, v in data.iteritems() if len(v) > 0}
            data = pd.Panel(data).transpose(0, 2, 1)
        else:
            data = pd.DataFrame(data).dropna(axis=1, how='any')
        return data

    def quotes(self, sids, start=None, end=None, select='close'):
        #TODO Fallback to 'close' if 'adjusted_close' not available
        sids = map(str.lower, map(str, sids))
        if start:
            start = rdb.epoch_time(intuition.utils.UTC_date_to_epoch(start))
        if end:
            #TODO Give a notice when given end is > database end
            end = rdb.epoch_time(intuition.utils.UTC_date_to_epoch(end))
        else:
            end = rdb.now()
        if select == 'ohlc':
            #TODO Handle 'adjusted_close'
            select = ['open', 'high', 'low', 'close', 'volume']
        if isinstance(select, str):
            select = [select]

        return self._load_quotes(sids, start, end, select)

    def random_tables(self, n=1000):
        log.info('generating random list of {} tables'.format(n))
        tables = rdb.table_list().run(self.session)
        random.shuffle(tables)
        return map(str, tables[:n])

    def load_portfolio(self, name):
        '''
        Build zipline.Portfolio object from <name> stored in database
        '''
        pass

    #def __del__(self):
        #FIXME RqlClientError(u'MALFORMED PROTOBUF (missing field
        #`type`):\ntoken: 508\n1: 4\n5: 1\n')
        #self.session.close()


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
