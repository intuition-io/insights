import os
import re
import pandas as pd
import rpy2.robjects as robjects

from intuition.zipline.portfolio import PortfolioFactory
import insights.transforms as transforms


class OptimalFrontier(PortfolioFactory):
    '''
    Computes with R the efficient frontier and pick up the optimize point on it
    '''
    def initialize(self, parameters):
        # R stuff: R functions file and rpy interface
        self.r = robjects.r
        portfolio_opt_file = '/'.join(
            [os.path.expanduser('~/.intuition'), 'R', 'opt_utils.R'])
        assert os.path.exists(portfolio_opt_file)
        self.r('source("{}")'.format(portfolio_opt_file))

        self.price_transform = transforms.get_past_returns(
            refresh_period=parameters.get('refresh', 1),
            window_length=parameters.get('window', 50),
            compute_only_full=parameters.get('only_full', True))

    def optimize(self, date, to_buy, to_sell, parameters):
        allocations = {}

        # Considers only portfolio positions + future positions - positions
        # about to be sold
        #positions = set([p for p in self.portfolio.positions.keys()
                         #if self.portfolio.positions[p].amount]
                        #).union(to_buy.keys()).difference(to_sell.keys())

        for sid in to_sell:
            allocations[sid] = -parameters.get('perc_sell', 1.0)

        if len(to_buy) == 1:
            allocations.update(
                {to_buy.keys()[0]: parameters.get('max_weigths', 0.2)})
            return allocations, 0, 1

        if 'historical_returns' in parameters:
            returns_df = parameters['historical_returns']
            #if not len(returns_df):
                #return allocations, 0, 1
        else:
            returns_df = self.price_transform.handle_data(to_buy)
        if returns_df is None:
            return allocations, 0, 1

        # Remove incomplete data
        for i, column in enumerate(returns_df):
            if returns_df[column].isnull().any():
                self.log.warning('missing data for {}, ignoring'
                                 .format(column))
                returns_df = returns_df.dropna(axis=1)

        returns = pd.rpy.common.convert_to_r_matrix(returns_df)
        frontier = self.r('getEfficientFrontier')(
            returns, points=500, Debug=False, graph=False)

        if not frontier:
            self.log.warning('No optimal frontier found')
            return allocations, 0, 1

        try:
            mp = self.r('marketPortfolio')(
                frontier, 0.02, Debug=False, graph=False)
        except:
            self.log.error('error running R optimizer')
            return allocations, 0, 1

        #FIXME Some key errors survive so far
        for sid in returns_df:
            #NOTE R change a bit names
            try:
                allocations[sid] = round(
                    mp.rx(re.sub("[-,!\ ]", ".", sid))[0][0], 2)
            except:
                allocations[sid] = 0.00

        er = round(mp.rx('er')[0][0], 2)
        eStd = round(mp.rx('eStd')[0][0], 2)
        self.log.info(
            'Allocation: {} With expected return: {} and expected risk: {}'
            .format(allocations, er, eStd))

        return allocations, er, eStd
