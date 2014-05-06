# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Database utils
  --------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: %LICENCE%, see LICENSE for more details.
'''

import os
import copy

# We will use these settings later in the code to
# connect to the RethinkDB server.
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 28015),
    'db': os.getenv('DB_NAME', 'intuition'),
    'user': os.getenv('DB_USER', 'quant'),
    'password': os.getenv('DB_PASSWORD', 'ity')
}


def portfolio_to_dict(portfolio):
    json_pf = copy.deepcopy(portfolio).__dict__
    if json_pf['positions']:
        for sid, infos in portfolio.positions.iteritems():
            json_pf['positions'][sid] = infos.__dict__
    return json_pf
