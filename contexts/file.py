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


import os
import datetime
import pytz

import intuition.data.utils as datautils
import intuition.utils.dates as datesutils


Regex = "*\.[yml|json]"
default_dir = '/'.join([os.environ['HOME'], '.intuition'])


def _load_context(storage):
    if storage.find('intuition') != -1:
        # We got a relative path, try at the default location
        storage = '/'.join([default_dir, storage.split('/')[-1]])
    if storage.find('json') > 0:
        fmt_module = __import__('json')
    elif storage.find('yaml') > 0:
        fmt_module = __import__('yaml')
    else:
        raise NotImplementedError('unsupported file format: %s' % storage)

    try:
        context = fmt_module.load(open(storage, 'r'))
    except IOError, e:
        print('loading json configuration: %s', e)
        context = {}

    return context


def _normalize_context(context):
    if 'start' in context:
        if isinstance(context['start'], datetime.date):
            context['start'] = datetime.date.strftime(
                context['start'], format='%Y-%m-%d')
    if 'end' in context:
        if isinstance(context['end'], datetime.date):
            context['end'] = datetime.date.strftime(
                context['end'], format='%Y-%m-%d')

    exchange = datautils.detect_exchange(context['universe'])

    dummy_dates = datesutils.build_date_index(
        context.pop('start', ''), context.pop('end', ''))
    #TODO Use zipline style to filter instead
    trading_dates = datautils.filter_market_hours(dummy_dates, exchange)

    context['exchange'] = exchange
    context['index'] = trading_dates
    context['live'] = (datetime.datetime.now(tz=pytz.utc) < trading_dates[-1])


def build_context(storage):
    context = _load_context(storage)

    algorithm = context.pop('algorithm', {})
    manager = context.pop('manager', {})

    _normalize_context(context)

    if not len(context['index']):
        print('! Market closed.')
        context = algorithm = manager = {}

    return context, algorithm, manager
