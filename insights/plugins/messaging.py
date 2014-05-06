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


import redis
import json
import os


BROKER_CONFIG = {
    'host': os.getenv('BROKER_HOST', 'localhost'),
    'port': int(os.getenv('BROKER_PORT', 6379)),
}


class RedisProtocol():
    '''
    Messaging skills for algorithms
    It uses redis to listen for incoming messages and publish informations
    Goal is to provide algo <-> algo and user <-> algo communication

    redis 172.17.0.3:6379> rpush "intuition" "{'JRA': 12}"
    '''

    # How much time are we waiting for incoming messages
    timeout = 1

    def __init__(self, channel='intuition'):
        self.channel = channel
        self.client = redis.StrictRedis(
            host=BROKER_CONFIG['host'], port=BROKER_CONFIG['port'], db=0)

    def check(self, order, sids):
        ''' Check if a message is available '''
        payload = "{}"
        #TODO store hashes {'intuition': {'id1': value, 'id2': value}}
        # Block self.timeout seconds on self.channel for a message
        raw_msg = self.client.blpop(self.channel, timeout=self.timeout)
        if raw_msg:
            _, payload = raw_msg

            msg = json.loads(payload.replace("'", '"'), encoding='utf-8')
            for sid in msg.keys():
                #TODO Harmonize lower() and upper() symbols
                if sid.lower() in map(str.lower, sids):
                    print('ordering {} of {}'.format(msg[sid], sid))
                    #order(sid.upper(), msg[sid])
                    order(sid, msg[sid])
                else:
                    print('skipping unknown symbol {}'.format(sid))

    def emit(self, data):
        #NOTE Someway to control the correct execution ?
        self.client.rpush(self.channel, data)
