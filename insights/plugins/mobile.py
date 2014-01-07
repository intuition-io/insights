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


def push_to_android(api_key, device_id, payload, push_type):
    ''' Push android notification through www.pushbullet.com '''
    payload['type'] = push_type
    payload['device_id'] = device_id
    return requests.post('https://api.pushbullet.com/api/pushes',
                         data=payload,
                         auth=(api_key, ''))


class AndroidPush():
    '''
    Push Android push notifications
    https://www.pushbullet.com/api
    '''

    api_url = 'https://api.pushbullet.com/api/'
    device = None

    def __init__(self, device_name):
        try:
            self.api_key = os.environ['PUSHBULLET_API_KEY']
        except KeyError:
            self.api_key = ''
        self.device = self._device_lookup(device_name)

    def _device_lookup(self, device_name):
        ''' Request informations about <name> device '''
        device_found = {}
        response = requests.get(self.api_url + 'devices',
                                auth=(self.api_key, ''))
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
            raise NotImplementedError()
        elif 'items' in payload:
            push_type = 'list'
        elif 'body' in payload:
            push_type = 'note'
        return push_type

    def push(self, payload, push_type=None):
        if push_type is None:
            push_type = self._detect_push_type(payload)
        return push_to_android(self.api_key,
                               self.device['id'],
                               payload,
                               push_type)
