# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

from zipline.transforms.batch_transform import batch_transform


@batch_transform
def get_past_prices(data):
    return data['price']


@batch_transform
def get_past_returns(data):
    '''
    Parameters: data
        pandas.panel (major: index, minor: sids)
    '''
    returns_df = data['price'].pct_change()
    # Because of return calculation, first raw is nan
    #FIXME nan values remain anyway
    #return np.nan_to_num(returns_df.values[1:])
    return returns_df.fillna(0.0)
