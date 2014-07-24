# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Machine learning technics
  -------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import datetime as dt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.qda import QDA
from intuition.api.algorithm import TradingFactory
from insights.algorithms.utils import common_middlewares
import insights.transforms as transforms
from insights.plugins.database.rethink import RethinkdbFinance


# TODO Use a period test to measure accuracy
# TODO Use cross-validation to reduce fitting error
# TODO More advanced forecasting with ANN and SVM
class ForecastEngine(object):

    models = {
        'LR': LogisticRegression(),
        'LDA': LDA(),
        'QDA': QDA()
    }

    def __init__(self, sids, end, loopback=30):
        # TODO Change sid for a more generic name
        self.sids = sids
        db = RethinkdbFinance(db='quotes')
        start = end - dt.timedelta(days=loopback)
        self.raw_data = db.quotes(
            sids, start=start, end=end
        )

    def _build_lagged_series(self, sid, lags=3):
        data = self.raw_data[sid]
        tslag = pd.DataFrame(index=data.index)
        tsret = pd.DataFrame(index=data.index)

        for i in xrange(lags):
            tslag['lag%s' % str(i + 1)] = data['adjusted_close'].shift(i + 1)

        tsret['returns'] = data['adjusted_close'].pct_change() * 100.0

        # If any of the values of percentage returns equal zero, set them to
        # a small number (stops issues with QDA model in scikit-learn)
        for i, x in enumerate(tsret['returns']):
            if (abs(x) < 0.0001):
                tsret['returns'][i] = 0.0001

        # Create the lagged percentage returns columns
        for i in xrange(lags):
            tsret['lag%s' % str(i + 1)] = \
                tslag['lag%s' % str(i + 1)].pct_change() * 100.0

        tsret['direction'] = np.sign(tsret['returns'])
        return tsret[lags:]

    def fit_model(self, sid, model='QDA', lags=3):
        data = self._build_lagged_series(sid, lags=lags)
        # Use the prior two days of returns as predictor values, with direction
        # as the response
        X_train = data[['lag1', 'lag2']]
        y_train = data['direction']

        # Create the model and the forecasting strategy
        model = self.models[model.upper()]
        try:
            model.fit(X_train, y_train)
        except Exception as error:
            # Some data errors remain and we have juste 1 or -1
            # TODO The algo goes on anyway but the result are not reliable
            print 'model fitting failed for {}: {}'.format(
                sid, error
            )
        return model


# http://www.quantstart.com/articles/Forecasting-Financial-Time-Series-Part-1
# Backtesting-a-Forecasting-Strategy-for-the-SP500-in-Python-with-pandas
class SNPForecast(TradingFactory):
    '''
    doc: |
      ...
    parameters:
      refresh_period: period to recompute signals [default 5]
      model: |
        Machine learning algorithm to use between QDA, LDA and LR [default QDA]
      loopback: Period of time prior backtest to train the model [default 30]
      window: Days of past data used for new predictions [default ]
    '''

    def initialize(self, properties):
        # Interactive, mobile, hipchat, database and commission middlewares
        for middleware in common_middlewares(properties, self.identity):
            self.use(middleware['func'], middleware['backtest'])

        self.refresh_period = int(properties.get('refresh_period', 5))
        self.loopback = int(properties.get('loopback', 30))
        self.model = properties.get('model', 'qda')

        # data loopback for fitted models
        self.lags_transform = transforms.get_lags_returns(
            window_length=int(properties.get('window', 40)),
            compute_only_full=properties.get('only_full')
        )

    def warm(self, data):
        self.last_data = {
            sid: {'price': data[sid].price, 'prediction': 0.0} for sid in data
        }

        forecaster = ForecastEngine(
            sids=data.keys(),
            end=self.perf_tracker.period_start,
            loopback=self.loopback
        )

        self.models = {
            sid: forecaster.fit_model(sid, model=self.model)
            for sid in data.keys()
        }

    def event(self, data):
        signals = {'buy': {}, 'sell': {}}
        recorded_state = {}

        lags_returns = self.lags_transform.handle_data(data)
        if lags_returns is None or \
                self.elapsed_time.days % self.refresh_period != 0:
            return signals

        for sid in data:
            predict = self.models[sid].predict(
                lags_returns[sid][['lag1', 'lag2']]
            )
            signal = np.diff(predict)[-1] / 2.0
            actual = np.sign(data[sid].price - self.last_data[sid]['price'])

            recorded_state[sid] = {
                'price': data[sid].price,
                'signals': {
                    'prediction': self.last_data[sid]['prediction'],
                    'actual': actual
                }
            }

            if signal > 0:
                signals['buy'][sid] = data[sid]
                recorded_state[sid]['msg'] = (
                    'Buying {}: positive prediction'.format(sid)
                )
            elif signal < 0:
                signals['sell'][sid] = data[sid]
                recorded_state[sid]['msg'] = (
                    'Selling {}: negative prediction'.format(sid)
                )

            self.last_data[sid] = {
                'price': data[sid].price, 'prediction': signal
            }

        self.record(**recorded_state)
        return signals
