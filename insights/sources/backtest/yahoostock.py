#
# Copyright 2013 Quantopian, Inc.
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


from intuition.zipline.data_source import DataFactory
import intuition.data.remote as remote


class YahooPriceSource(DataFactory):
    """
    Fetchs prices for the given sids from yahoo.com
    """
    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'volume': (int, 'volume'),
        }

    def get_data(self):
        return remote.Data().fetch_equities_daily(
            self.sids, indexes={}, start=self.start, end=self.end)


class YahooOHLCSource(DataFactory):
    """
    Fetchs OHLC data for the given sids from yahoo.com
    """
    @property
    def mapping(self):
        mapping = {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'volume': (int, 'volume'),
        }

        # Add additional fields.
        for field_name in self.data.minor_axis:
            if field_name in ['price', 'volume', 'dt', 'sid']:
                continue
            mapping[field_name] = (lambda x: x, field_name)
        return mapping

    def get_data(self):
        return remote.Data().fetch_equities_daily(
            self.sids, ohlc=True, indexes={}, start=self.start, end=self.end)
