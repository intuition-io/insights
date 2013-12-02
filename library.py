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


from neuronquant import FollowTrend,RegularRebalance
from neuronquant import StochasticGradientDescent
from neuronquant import DualMovingAverage,VolumeWeightAveragePrice,Momentum,MovingAverageCrossover
from neuronquant import AutoAdjustingStopLoss
from neuronquant import MarkovGenerator
from neuronquant import StddevBased
from neuronquant import Constant
from neuronquant import Fair
from neuronquant import GlobalMinimumVariance
from neuronquant import OptimalFrontier
from neuronquant import CSVSource
from neuronquant import DBPriceSource
from neuronquant import QuandlSource
from neuronquant import YahooPriceSource,YahooOHLCSource
from neuronquant import EquitiesLiveSource
from neuronquant import ForexLiveSource


algorithms = {'FollowTrend': FollowTrend,'RegularRebalance': RegularRebalance,'StochasticGradientDescent': StochasticGradientDescent,'DualMovingAverage': DualMovingAverage,'VolumeWeightAveragePrice': VolumeWeightAveragePrice,'Momentum': Momentum,'MovingAverageCrossover': MovingAverageCrossover,'AutoAdjustingStopLoss': AutoAdjustingStopLoss,'MarkovGenerator': MarkovGenerator,'StddevBased': StddevBased,}

portfolio_managers = {'Constant': Constant,'Fair': Fair,'GlobalMinimumVariance': GlobalMinimumVariance,'OptimalFrontier': OptimalFrontier,}

data_sources = {}
