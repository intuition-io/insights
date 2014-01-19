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


import pymongo
import datetime
import pytz

import intuition.data.utils as datautils
import intuition.utils.dates as datesutils


database = 'intuition'
collection = 'contexts'


# Super interface: http://genghisapp.com/
def _load_context(storage):
    tmp = storage.split('/')
    uri = tmp[0]
    conf_id = tmp[1]
    client = pymongo.MongoClient("mongodb://{}/".format(uri))
    assert (database in client.database_names())
    db = client[database]
    print 'connected to {} database'.format(db.name)
    assert (collection in db.collection_names())
    conf_doc = db[collection]
    print 'got {} document'.format(conf_doc.name)
    context = conf_doc.find_one({'id': conf_id})
    assert context

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


def build_context(storage):
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
    return context, {'algorithm': algorithm, 'manager': manager}
