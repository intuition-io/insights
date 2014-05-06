# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Rethinkdb plugin
  ----------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

import pytz
import datetime as dt
import random
from clint.textui import progress
import pandas as pd
import rethinkdb as rdb
import dna.logging
import dna.time_utils
from intuition.data.quandl import DataQuandl
import intuition.data.utils as datautils
import insights.plugins.database.utils as dbutils


log = dna.logging.logger(__name__)


class RethinkdbBackend(object):
    ''' Low level of rethinkdb management '''

    def __init__(self, **kwargs):
        host = kwargs.get('host', dbutils.DB_CONFIG['host'])
        port = kwargs.get('port', dbutils.DB_CONFIG['port'])
        db = kwargs.get('db', dbutils.DB_CONFIG['db'])
        self.table = kwargs.get('table', None)

        try:
            self.session = self._connection(host, port, db)
        except rdb.RqlDriverError, error:
            log.error(error)
            raise

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

    def available(self, table):
        # TODO Check with dates
        return datautils.clean_sid(table) in rdb.table_list().run(self.session)

    def random_tables(self, n=1000):
        log.info('generating random list of {} tables'.format(n))
        tables = rdb.table_list().run(self.session)
        random.shuffle(tables)
        return map(str, tables[:n])

    def last_chrono_entry(self, table):
        return rdb.table(datautils.clean_sid(table))\
            .order_by(rdb.desc('date'))\
            .limit(1)\
            .pluck(['date'])\
            .run(self.session)[0]

    #def __del__(self):
        #FIXME RqlClientError(u'MALFORMED PROTOBUF (missing field
        #`type`):\ntoken: 508\n1: 4\n5: 1\n')
        #self.session.close()


class RethinkdbFinance(RethinkdbBackend):
    '''
    Adds RethinkDB database backend to the portfolio
    '''

    def save_portfolio(self, datetime, portfolio, perf_tracker, recorded_vars):
        '''
        Store in Rethinkdb a zipline.Portfolio object
        '''
        if perf_tracker.progress != 0.0 and self.table:

            metrics = perf_tracker.to_dict()
            metrics.update({
                'date': datetime,
                'recorded': recorded_vars,
                'portfolio': dbutils.portfolio_to_dict(portfolio)
            })

            log.debug('Saving metrics in database')
            log.debug(
                rdb.table(self.table)
                   .insert(metrics)
                   .run(self.session)
            )

    def save_quotes(self, table, data, metadata={}, reset=False):
        table = datautils.clean_sid(table)
        if reset:
            self._reset_data(table)
        length = len(data)
        for date, row in progress.bar(data.iterrows(), expected_size=length):
            record = row.to_dict()
            record.update({'date': date})
            record.update(metadata)
            report = rdb.table(table).insert(record).run(self.session)
            assert not report['errors']

    def _load_quotes(self, sids, start, end, select):
        is_panel = not len(select) == 1
        data = {}
        for table in sids:
            if not self.available(table):
                log.warning('{} not found in database, skipping'
                            .format(table))
                continue

            if select:
                select.append('date')
                cursor_data = rdb.table(datautils.clean_sid(table))\
                    .filter(lambda row: row['date'].during(
                            start, end))\
                    .pluck(select)\
                    .run(self.session)
            else:
                # TODO pop 'id' field
                cursor_data = rdb.table(datautils.clean_sid(table))\
                    .filter(lambda row: row['date'].during(
                            start, end))\
                    .run(self.session)

            data[table] = {}
            for row in cursor_data:
                # Remove rethinkdb automatic id
                row.pop('id', None)
                # tzinfo of the object is rethinkdb specific
                date = row.pop('date').astimezone(pytz.utc)
                data[table][date] = row if is_panel else row[select[0]]

        if is_panel:
            # FIXME Missing data
            data = {k: v for k, v in data.iteritems() if len(v) > 0}
            data = pd.Panel(data).transpose(0, 2, 1)
        else:
            data = pd.DataFrame(data).fillna(method='pad')
        return data

    def quotes(self, sids, start=None, end=None, select=[]):
        #sids = map(str.lower, map(str, sids))
        if start:
            start = rdb.epoch_time(dna.time_utils.UTC_date_to_epoch(start))
        if end:
            # TODO Give a notice when given end is > database end
            end = rdb.epoch_time(dna.time_utils.UTC_date_to_epoch(end))
        else:
            end = rdb.now()
        if select == 'ohlc':
            # TODO Handle 'adjusted_close'
            select = ['open', 'high', 'low', 'close', 'volume']
        if not isinstance(select, list):
            select = [select]

        return self._load_quotes(sids, start, end, select)


class Keeper(object):
    ''' Fill and synchronize database '''

    def __init__(self, db='quotes'):
        self.db = RethinkdbFinance(db=db)

        log.info('using {} as data provider'.format('quandl.com'))
        self.feed = DataQuandl()

    def _store(self, sid, data):
        if not data.isnull().any().any():
            log.info('saving {} in database'.format(sid))
            self.db.save_quotes(sid, data, {}, reset=self.reset)
        else:
            log.warning('{}: empty dataset'.format(sid))

    def fill_database(self, sids, start, end):
        if isinstance(end, str):
            start = dna.time_utils.normalize_date_format(start)
        if isinstance(end, str):
            end = dna.time_utils.normalize_date_format(end)
        self.reset = True
        self._download_and_store(sids, start, end)

    def sync(self, sids, start, end):
        # TODO Per quote sync
        younger_date = dt.datetime(3020, 1, 1, tzinfo=pytz.utc)
        for sid in sids:
            last_entry = self.db.last_chrono_entry(sid)
            if last_entry['date'] < younger_date:
                younger_date = last_entry['date']

        start = younger_date + dt.timedelta(1)
        end = dt.date.today()
        self.reset = False

        log.info('downloading {} data ({} -> {})'.format(sids, start, end))
        self._download_and_store(sids, start, end)

    def _download_and_store(self, sids, start, end):
        data = self.feed.fetch(
            sids, start=start, end=end, returns='pandas')

        for sid in data:
            try:
                self._store(sid=sid, data=data[sid])
            except Exception as error:
                log.error(error)
                continue
