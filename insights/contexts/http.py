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


# Can't make python-etcd to work currently
import etcd
import datetime
import pytz

import intuition.data.utils as datautils
import intuition.utils.dates as datesutils


def _load_context(storage):
    # storage = {{etcd_ip }}:{{ etcd_port }}/{{ conf_id }}
    context = {}
    tmp = storage.split('/')
    etcd_ip = tmp[0].split(':')[0]
    etcd_port = int(tmp[0].split(':')[1])
    conf_id = tmp[1]
    client = etcd.Client(host=etcd_ip, port=etcd_port)

    #TODO A beautiful recursive function
    for item in client.get('/' + conf_id):
        key_1 = item.key.split('/')[-1]
        if item.dir:
            context[key_1] = {}
            for subitem in client.get(item.key):
                context[key_1][subitem.key.split('/')[-1]] = subitem.value
        else:
            context[key_1] = item.value

    return context


def _normalize_context(context):
    exchange = datautils.detect_exchange(context['universe'])

    dummy_dates = datesutils.build_date_index(
        context.pop('start', ''), context.pop('end', ''))
    #TODO Use zipline style to filter instead
    trading_dates = datautils.filter_market_hours(dummy_dates, exchange)

    context['exchange'] = exchange
    context['index'] = trading_dates
    context['live'] = (datetime.datetime.now(tz=pytz.utc) < trading_dates[-1])

    if not len(context['index']):
        print('! Market closed.')
        context = {}


def _normalize_strategy(strategy):
    ''' etcd only retrieves strings, giving back right type '''
    for k, v in strategy.iteritems():
        if v == 'true':
            strategy[k] = True
        elif v == 'false':
            strategy[k] = False
        else:
            try:
                strategy[k] = float(v)
            except ValueError:
                pass


def build_context(storage):
    # Storage like {{ etcd_ip }}:{{ etcd_port }}/{{ conf_id }}
    try:
        context = _load_context(storage)
    except Exception as e:
        print('An exception occured : {} ({})'
              .format(e, type(e)))
        context = {}

    algorithm = context.pop('algorithm', {})
    manager = context.pop('manager', {})

    if context:
        _normalize_context(context)
    if algorithm:
        _normalize_strategy(algorithm)
    if manager:
        _normalize_strategy(manager)

    return context, {'algorithm': algorithm, 'manager': manager}
