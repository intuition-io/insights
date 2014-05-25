#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

import sys
import argparse
import datetime as dt
import pandas as pd
from clint.textui import puts, colored, indent
import dna.utils
import insights.test_framework as test_framework
import intuition.utils as utils
import intuition.data.remote as remote


# TODO More genric and use it with other scripts
class InsightsCli(object):
    ''' Starter point for Intuition based cli utilities '''

    description = ''

    def __init__(self):
        self.parser = argparse.ArgumentParser(description=self.description)
        self.parser.add_argument(
            '-V', '--version', action='version',
            version='%(prog)s v0.0.2 Licence Apache 2.0',
            help='Print program version'
        )
        self.parser.add_argument(
            '-v', '--verbose', action='store_true', help='Print logs on stdout'
        )
        self.parser.add_argument(
            '-s', '--start', action='store', default=None,
            help='start date for quotes'
        )
        self.parser.add_argument(
            '-e', '--end', action='store', default=dt.date.today(),
            help='end date for quotes'
        )

    @property
    def args(self):
        return self.parser.parse_args()

    def msg(self, body, indentation=2):
        with indent(indentation, 'info | '):
            puts(colored.blue(str(body)))

    def warning(self, body, indentation=2):
        with indent(indentation, 'warn | '):
            puts(colored.red(str(body)))


class Optimizer(InsightsCli):

    description = 'Allocation optimizer'

    def __init__(self):
        InsightsCli.__init__(self)
        self.parser.add_argument(
            '-m', '--manager', action='store',
            required=True, help='Portfolio manager to use'
        )
        self.parser.add_argument(
            '-b', '--buy', action='store',
            default='', help='sids to buy'
        )
        self.parser.add_argument(
            '-c', '--clear', action='store',
            default='', help='sids to sell like sid1:amount_owned,...'
        )

        self.signals = self._read_signals()

        # TODO init arg support
        self.manager = utils.intuition_module(
            '.'.join(['insights.managers', self.args.manager])
        )()
        self.manager.update(
            test_framework.generate_portfolio(self.signals['sell']),
            self.args.end
        )

    def load_historical_quotes(self):
        signals_ = self.signals
        raw_data_ = {
            sid: remote.historical_pandas_yahoo(sid, start=self.args.start)
            for sid in signals_['universe']
        }
        data = pd.DataFrame({
            sid: raw_data_[sid]['Adj Close'] for sid in signals_['universe']
        }).fillna(method='pad')

        self.msg('updating manager with quotes')
        self.manager.advise(historical_prices=data)

    def _read_signals(self):
        # TODO Use universe.Market when it will be able to parse explicit sids
        buy_sids = self.args.buy.split(',') if self.args.buy else []

        if self.args.clear:
            # TODO Check input
            sell_sids = {
                sid[0]: float(sid[1]) for sid in map(
                    lambda x: x.split(':'), self.args.clear.split(',')
                )
            }
        else:
            sell_sids = {}

        return {
            'buy': buy_sids,
            'sell': sell_sids,
            'universe': buy_sids + sell_sids.keys()
        }


def main():
    cli = Optimizer()

    cli.msg('- Intuition allocation optimizer')
    cli.warning('Only supports Global minimum variance for now\n', 4)

    if cli.args.start:
        cli.msg('downloading historical quotes ...')
        cli.load_historical_quotes()

    to_buy = {sid: 1 for sid in cli.signals['buy']}
    to_sell = {sid: 1 for sid in cli.signals['sell'].keys()}
    allocations, e_return, e_risk = cli.manager.optimize(to_buy, to_sell)

    cli.msg('\nOptimization done.\n')
    cli.msg('Exprected return: {}'.format(e_return))
    cli.msg('Exprected risk: {}'.format(e_risk))
    for sid, alloc in allocations.iteritems():
        alloc = dna.utils.truncate(alloc, 3)
        cli.msg('{}: {}'.format(sid, alloc), 12)


if __name__ == '__main__':
    sys.exit(main())
