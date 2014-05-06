# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Influxdb plugin
  ---------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

from influxdb import client as influxdb
import dna.logging
import dna.time_utils
import insights.plugins.database.utils as dbutils


log = dna.logging.logger(__name__)


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
            dbutils.DB_CONFIG['host'], dbutils.DB_CONFIG['port'],
            dbutils.DB_CONFIG['user'], dbutils.DB_CONFIG['password'],
            dbutils.DB_CONFIG['db'])

    def save_portfolio(self, datetime, portfolio):
        '''
        Store in Rethinkdb a zipline.Portfolio object
        '''
        log.debug('Saving portfolio in database')
        pf = dbutils.portfolio_to_dict(portfolio)
        pf.pop('positions')
        data = [{
            "name": self.name,
            "time": datetime.strftime("%Y-%m-%d %H:%M"),
            "columns": pf.keys(),
            "points": [pf.values()]}]
        # Timestamp type is not json serializable
        data[0]['points'][0][-1] = pf['start_date'].__str__()

        self.session.write_points(data)
