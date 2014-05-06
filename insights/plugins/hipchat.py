# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  hipchat Bot
  -----------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''


import os
import requests
import dna.logging

log = dna.logging.logger(__name__)


class Bot(object):
    '''
    Hipchat api client that sends notifications to a specified room
    Doc: https://www.hipchat.com/docs/api
    '''

    api_key = os.environ.get('HIPCHAT_API')
    api_url = 'https://api.hipchat.com/v1'
    name = 'Intuition Bot'
    bg_color = 'green'
    intro = 'Hey guys, I detected an opportunity'

    def __init__(self, room_id, name=None, api_key=None):
        self.room_id = room_id
        if api_key:
            self.api_key = api_key
        if name:
            self.name = name

    def _test_token(self):
        ''' TODO '''
        pass

    def _api_call(self, path, data={}, http_method=requests.get):
        ''' Process an http call against the hipchat api '''
        log.info('performing api request', path=path)
        response = http_method('/'.join([self.api_url, path]),
                               params={'auth_token': self.api_key},
                               data=data)
        log.debug('{} remaining calls'.format(
            response.headers['x-ratelimit-remaining']))
        return response.json()

    def message(self, body, room_id, style='text'):
        ''' Send a message to the given room '''
        # TODO Automatically detect body format ?
        path = 'rooms/message'
        data = {
            'room_id': room_id,
            'message': body,
            'from': self.name,
            'notify': 1,
            'message_format': style,
            'color': self.bg_color
        }
        log.info('sending message to hipchat', message=body, room=room_id)
        feedback = self._api_call(path, data, requests.post)
        log.debug(feedback)
        return feedback

    def notify(self, datetime, orderbook):
        # TODO Same flood security as mobile
        if orderbook:
            body = '<strong>{} - {}</strong><ul><li>{}</li></ul>'.format(
                datetime,
                self.intro,
                '</li><li>'.join(
                    ['{}: {}'.format(sid, quantity)
                        for sid, quantity in orderbook.iteritems()])
            )
            self.message(body, self.room_id, style='html')
