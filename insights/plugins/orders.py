# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Trade transactions
  ------------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''


class SimpleExecution(object):
    '''
    Simpler orderbook processing.
    '''

    def process(self, orderbook, order, order_percent, datetime, logger):
        ''' Execute transactions based on computed orderbook '''
        for stock, alloc in orderbook.iteritems():
            logger.debug(
                '{}: Ordered {} {} stocks'.format(datetime, stock, alloc)
            )
            if isinstance(alloc, int):
                order(stock, alloc)
            elif isinstance(alloc, float) and \
                    alloc >= -1 and alloc <= 1:
                order_percent(stock, alloc)
            else:
                logger.debug('{}: invalid order for {}: {})'
                             .format(datetime, stock, alloc))
