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
    #import ipdb; ipdb.set_trace()
    # Because of return calculation, first raw is nan
    #FIXME nan values remain anyway
    #return np.nan_to_num(returns_df.values[1:])
    return returns_df.fillna(0.0)
