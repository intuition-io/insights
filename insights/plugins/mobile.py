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


import requests
import os
import time


def push_to_android(api_key, device_id, payload, push_type):
    ''' Push android notification through www.pushbullet.com '''
    payload['type'] = push_type
    payload['device_id'] = device_id
    return requests.post('https://api.pushbullet.com/api/pushes',
                         data=payload,
                         auth=(api_key, ''))


class AndroidPush():
    '''
    Push Android notifications
    https://www.pushbullet.com/api
    '''

    _api_url = 'https://api.pushbullet.com/api/'
    device = None
    _count = 0
    _rate_limit = 10
    _min_interval = 30
    _last_time = -30

    def __init__(self, device_name):
        try:
            self._api_key = os.environ['PUSHBULLET_API_KEY']
        except KeyError:
            self._api_key = ''
        self.device = self._device_lookup(device_name)

    def _device_lookup(self, device_name):
        ''' Request informations about <name> device '''
        device_found = {}
        response = requests.get(self._api_url + 'devices',
                                auth=(self._api_key, ''))
        if response.ok:
            for device in response.json()['devices']:
                if device_name == device['extras']['model']:
                    #TODO Check device['extras']['nickname'] as well
                    device_found = device
        return device_found

    def _detect_push_type(self, payload):
        push_type = ''
        if 'url' in payload:
            push_type = 'link'
        elif 'address' in payload:
            push_type = 'address'
        elif 'file' in payload:
            push_type = 'file'
            #TODO File push needs multi-part form encoding
            raise NotImplementedError('file payload is not yet supported')
        elif 'items' in payload:
            push_type = 'list'
        elif 'body' in payload:
            push_type = 'note'
        else:
            raise ValueError('invalid push payload')
        return push_type

    def push(self, payload, push_type=None):
        if push_type is None:
            push_type = self._detect_push_type(payload)
        return push_to_android(self._api_key,
                               self.device['id'],
                               payload,
                               push_type)

    def _watchdog(self):
        ''' Notifications are stopped if
          * The last one was too close
          * We reach a rated limit '''
        too_early = (time.time() - self._last_time < self._min_interval)
        too_much = (self._count >= self._rate_limit)
        return (False if (too_early or too_much) else True)

    def notify(self, orderbook):
        if orderbook and self._watchdog():
            # Alert user of the orders about to be processed
            # Ok... kind of fancy method
            #ords = {'-1': 'You should sell', '1': 'You should buy'}
            items = ['{} {} stocks of {}'.format(
                #ords[str(amount / abs(amount))], amount, ticker)
                ['buy', 'sell'][amount < 0], amount, ticker)
                for ticker, amount in orderbook.iteritems()
                if amount != 0]
            payload = {
                'title': 'Portfolio manager notification',
                'items': items,
            }
            req = self.push(payload)
            if req.ok:
                data = req.json()
                print('successfully notified with id {}:{} at {}'
                      .format(data['receiver_id'],
                              data['id'],
                              data['created']))
                req.close()
            self._count += 1
            self._last_time = time.time()
