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
import pytz
import pandas as pd

from intuition.zipline.data_source import DataFactory


class CSVSource(DataFactory):
    """
    Loads a dataframe or a panel from given csv file(s)
    csv files must be located in ~/.intuition/data
    """

    def get_data(self):
        tmp_data = {}
        for sid in self.sids:
            if sid.rfind('csv') == -1:
                sid += '.csv'
            file_path = '/'.join(
                [os.path.expanduser('~/.intuition'), 'data', sid])
            assert os.path.exists(file_path)

            df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
            # Make sure of chronological order
            df = df.sort_index()
            df = df[df.index >= self.start]
            df = df[df.index <= self.end]
            df.index = df.index.tz_localize(pytz.utc)
            tmp_data[sid] = df

        if len(self.sids) == 1:
            data = tmp_data[sid]
        else:
            data = pd.Panel(tmp_data)
        return data

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'Adjusted Close'),
            'volume': (int, 'Volume'),
            'open': (float, 'Open'),
            'high': (float, 'High'),
            'low': (float, 'Low'),
            'close': (float, 'Close')
        }
