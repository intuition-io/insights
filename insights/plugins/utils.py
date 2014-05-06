# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Util plugins
  ------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''


def debug_portfolio(logger, datetime, portfolio):
    logger.debug('[{}] {}'.format(datetime, portfolio))


def debug_metrics(logger, datetime, perf_tracker):
    if perf_tracker.progress != 0.0:
        logger.debug('[{}] {}'.format(
            datetime, perf_tracker.cumulative_risk_metrics.to_dict()))
