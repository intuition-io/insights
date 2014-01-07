#
# Copyright 2013 Xavier Bruhiere
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


import logbook
import random
import pandas as pd

from intuition.zipline.data_source import LiveDataFactory


log = logbook.Logger('intuition.sources.live.fake')


class FakeLiveSource(LiveDataFactory):
    """
    At each event datetime of the provided index, FakeLiveSource
    generates random prices
    """

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'volume': (int, 'volume'),
        }

    def _feed_random_data(self):
        return {
            'price': 100 * random.random(),
            'volume': 10000 * random.random()
            }

    def get_data(self):
        data = {}
        for sid in self.sids:
            data[sid] = self._feed_random_data()

        return pd.DataFrame(data)
