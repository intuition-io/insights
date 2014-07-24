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
import insights.plugins.orders as orders


def common_middlewares(properties, identity):
    middlewares = []

    if properties.get('orders'):
        middlewares.append({
            'func': orders.SimpleExecution().process,
            'backtest': True
        })

    if properties.get('save'):
        middlewares.append({
            'func': database.RethinkdbFinance(
                table=identity, db='portfolios', reset=True).save_portfolio,
            'backtest': True
        })

    if properties.get('interactive'):
        middlewares.append({
            'func': msg.RedisProtocol(identity).check,
            'backtest': True
        })

    device = properties.get('mobile')
    if device:
        middlewares.append({
            'func': mobile.AndroidPush(device).notify,
            'backtest': False
        })

    hipchat_room = properties.get('hipchat')
    if hipchat_room:
        middlewares.append({
            'func': hipchat.Bot(hipchat_room, name=identity).notify,
            'backtest': False
        })

    return middlewares
