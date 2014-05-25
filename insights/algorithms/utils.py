# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Algorithm utilities
  -------------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

import insights.plugins.database.rethink as database
import insights.plugins.mobile as mobile
import insights.plugins.hipchat as hipchat
import insights.plugins.messaging as msg


def common_middlewares(properties, identity):
    middlewares = []

    if properties.get('interactive'):
        middlewares.append(msg.RedisProtocol(identity).check)

    device = properties.get('mobile')
    if device:
        middlewares.append(mobile.AndroidPush(device).notify)

    if properties.get('save'):
        middlewares.append(database.RethinkdbFinance(
            table=identity, db='portfolios', reset=True)
            .save_portfolio)

    hipchat_room = properties.get('hipchat')
    if hipchat_room:
        middlewares.append(hipchat.Bot(
            hipchat_room, name=identity).notify)

    return middlewares
