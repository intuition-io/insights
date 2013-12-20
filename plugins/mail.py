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


class Mailgun():
    '''
    Send emails through mailgun api
    '''
    api_url = 'https://api.mailgun.net/v2/{}/messages'
    api_key = ''

    def __init__(self, friendly_name, domain):
        self.from_email = '{} <me@{}>'.format(friendly_name, domain)
        self.api_url = self.api_url.format(domain)
        if 'MAILGUN_API_KEY' in os.environ:
            self.api_key = os.environ['MAILGUN_API_KEY']

    def send_mail(self, targets, subject, body):
        if isinstance(targets, str):
            targets = [targets]
        payload = {
            'from': self.from_email,
            'to': targets,
            'subject': subject,
            'text': body
        }
        return requests.post(self.api_url,
                             auth=('api', self.api_key),
                             data=payload)
