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


import redis
import json


class RedisMessaging():
    '''
    Messaging skills for algorithms
    It uses redis to listen for incoming messages and publish informations
    Goal is to provide algo <-> algo and user <-> algo communication
    '''

    # How much time are we waiting for incoming messages
    timeout = 1
    channel = 'intuition'

    def __init__(self, host='localhost', port=6379):
        self.client = redis.StrictRedis(host=host, port=port, db=0)

    def check(self):
        ''' Check if a message is available '''
        payload = "{}"
        # Block self.timeout seconds on self.channel for a message
        message = self.client.blpop(self.channel, timeout=self.timeout)
        if message:
            _, payload = message

        return json.loads(payload.replace("'", '"'), encoding='utf-8')

    def emit(self, data):
        #NOTE Someway to control the correct execution ?
        self.client.rpush(self.channel, data)
