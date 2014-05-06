# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Backtest data source loading csv files
  --------------------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import os
import pytz
import pandas as pd
import intuition.errors


# NOTE Current limitations
#   - One sid per csv file
#   - Every csv file must have the same structure
#   - Every csv file must have an index column
class PanelCSVSource(object):
    '''
    doc: Loads data from given csv file(s), one sid per file.
    parameters:
      path: custom path to search csv [default ~/.intuition/data/
      index_column: the header of the column holding dates [default Date]
    '''

    def __init__(self, sids=[], properties={}):
        self.index_col = properties.get('index_column', 'Date')
        self.custom_path = properties.get('path')

    def _filepath(self, sid):
        csv_dir = self.custom_path or os.path.join(
            os.path.expanduser('~/.intuition'), 'data')
        file_path = os.path.join(csv_dir, sid)
        if file_path.rfind('csv') == -1:
            file_path += '.csv'

        if not os.path.exists(file_path):
            raise intuition.errors.LoadDataFailed(
                reason='{} not found'.format(file_path), sids=sid)

        return file_path

    def get_data(self, sids, start, end):
        tmp_data = {}
        for sid in sids:

            file_path = self._filepath(sid)

            # Load the entire file
            df = pd.read_csv(
                file_path, index_col=self.index_col, parse_dates=True
            )
            # Try to store mapping fields
            self._fields = map(
                lambda x: x.lower().replace(' ', '_'), df.columns
            )

            # Make sure of chronological order
            df = df.sort_index()
            # Remove extra dates
            df = df[df.index >= start]
            df = df[df.index <= end]
            # Make it UTC aware
            df.index = df.index.tz_localize(pytz.utc)
            tmp_data[sid] = df

        if len(sids) == 1:
            data = tmp_data[sid]
        else:
            data = pd.Panel(tmp_data)
        return data

    @property
    def mapping(self):
        # Try to dynamically read fields
        mapping_struct = {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
        }
        # We need a field to be the standard price
        if 'adjusted_close' in self._fields:
            mapping_struct['price'] = \
                (float, self._fields.pop(self._fields.index('adjusted_close')))
        elif 'low' in self._fields:
            mapping_struct['price'] = \
                (float, self._fields.pop(self._fields.index('low')))
        else:
            raise NotImplementedError(
                'only support low and adjusted_close as price')

        for field in self._fields:
            mapping_struct[field] = (float, field)

        return mapping_struct
