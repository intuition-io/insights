#
# Copyright 2013 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# !!
# This file has been automatically generated
# Don't edit it manually, use update-library.sh script instead
# !!


import logbook


log = logbook.Logger('intuition.library')


from intuition.modules.algorithms.buyandhold import BuyAndHold
from intuition.modules.algorithms.gradient import StochasticGradientDescent
from intuition.modules.algorithms.momentum import Momentum
from intuition.modules.algorithms.movingaverage import DualMovingAverage
from intuition.modules.algorithms.rebalance import RegularRebalance
from intuition.modules.algorithms.stddev import StddevBased
from intuition.modules.algorithms.stoploss import AutoAdjustingStopLoss
from intuition.modules.algorithms.vwap import VolumeWeightAveragePrice
from intuition.modules.managers.constant import Constant
from intuition.modules.managers.fair import Fair
from intuition.modules.managers.gmv import GlobalMinimumVariance
from intuition.modules.managers.optimalfrontier import OptimalFrontier
from intuition.modules.sources.backtest.csv import CSVSource
from intuition.modules.sources.backtest.quandl import QuandlSource
from intuition.modules.sources.backtest.yahoostock import YahooPriceSource,YahooOHLCSource
from intuition.modules.sources.live.equities import EquitiesLiveSource
from intuition.modules.sources.live.fake import FakeLiveSource
from intuition.modules.sources.live.forex import ForexLiveSource


algorithms = {'BuyAndHold': BuyAndHold,'StochasticGradientDescent': StochasticGradientDescent,'Momentum': Momentum,'DualMovingAverage': DualMovingAverage,'RegularRebalance': RegularRebalance,'StddevBased': StddevBased,'AutoAdjustingStopLoss': AutoAdjustingStopLoss,'VolumeWeightAveragePrice': VolumeWeightAveragePrice,}

portfolio_managers = {'Constant': Constant,'Fair': Fair,'GlobalMinimumVariance': GlobalMinimumVariance,'OptimalFrontier': OptimalFrontier,}

data_sources = {'CSVSource': CSVSource,'QuandlSource': QuandlSource,'YahooPriceSource': YahooPriceSource,'YahooOHLCSource': YahooOHLCSource,'EquitiesLiveSource': EquitiesLiveSource,'FakeLiveSource': FakeLiveSource,'ForexLiveSource': ForexLiveSource,}


#TODO optimization algos

def check_availability(algo, manager, source):
  if algo not in algorithms:
    raise NotImplementedError('Algorithm {} not available or implemented'.format(algo))
  log.debug('Algorithm {} available, getting a reference on it.'.format(algo))

  if (manager) and (manager not in portfolio_managers):
    raise NotImplementedError('Manager {} not available or implemented'.format(manager))
  log.debug('Manager {} available, getting a reference on it.'.format(manager))

  if (source) and (source not in data_sources):
    raise NotImplementedError('Source {} not available or implemented'.format(source))
  log.debug('Source {} available'.format(source))

  return True
