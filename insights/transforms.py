# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import pandas as pd
import numpy as np
from zipline.transforms.batch_transform import batch_transform


@batch_transform
def get_past_prices(data):
    return data['price']


@batch_transform
def get_past_returns(data):
    returns_df = data['price'].pct_change()
    # Because of return calculation, first raw is nan
    # FIXME nan values remain anyway
    # return np.nan_to_num(returns_df.values[1:])
    return returns_df.fillna(0.0)


# NOTE This is a duplication of the ForecastEngine
@batch_transform
def get_lags_returns(data):
    '''
    Parameters: data
        pandas.panel (major: index, minor: sids)
    '''
    # TODO It should be a parameter exposed to the algo
    lags = 3
    lagged_series = {}
    for sid in data.minor_axis:
        # TODO Make it a function
        sid_window = data.minor_xs(sid)
        tslag = pd.DataFrame(index=data.major_axis)

        for i in xrange(lags):
            tslag['lag%s' % str(i + 1)] = sid_window['price'].shift(i + 1)

        tsret = pd.DataFrame(index=tslag.index)
        tsret['returns'] = sid_window['price'].pct_change() * 100.0

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
        lagged_series[sid] = tsret.fillna(0.0)

    return pd.Panel(lagged_series)
