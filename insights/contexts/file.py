# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  File context
  ------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache 2.0, see LICENSE for more details.
'''

import intuition.utils
import intuition.constants
from intuition.api.context import ContextFactory


class FileContext(ContextFactory):
    '''
    Fetch the configuration from json or yaml flat files. It expects an input
    like : <path/to/file.{json,yml,yaml}> and supports relative and absolute
    path.
    However, if the first directory provided is 'intuition', it will
    search for the file into ~/.intuition.
    '''

    def initialize(self, storage):
        config_file = storage['path'][-1]
        if storage['path'][0] == 'intuition':
            # We got a relative path, try at the default location
            storage['path'][0] = intuition.constants.DEFAULT_HOME
        self.configfile = '/'.join(storage['path'])

        if config_file.find('json') > 0:
            self.fmt_module = __import__('json')
        elif (config_file.find('yaml') > 0) or (config_file.find('yml') > 0):
            self.fmt_module = __import__('yaml')
        else:
            raise NotImplementedError(
                'unsupported file format: %s' % config_file)

    def load(self):
        try:
            context = self.fmt_module.load(open(self.configfile, 'r'))
        except IOError, error:
            raise ValueError(
                'loading configuration file: {} ({})'.format(
                    error, self.configfile))

        return context
