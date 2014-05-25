# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Packaging
  ---------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import os
from glob import glob
from setuptools import setup, find_packages

from insights import __version__, __author__, __licence__


requires = [
    'numpy>=1.8.1',
    'patsy>=0.2.1',
    'clint>=0.3.7',
    'python-etcd>=0.3.0',
    'redis>=2.9.1',
    'rpy2>=2.3.10',
    'pymongo>=2.7.1',
    'PyYAML>=3.11',
    'rethinkdb>=1.12.0-2',
    'scipy>=0.14.0',
    'pandas>=0.13.1',
    'influxdb>=0.1.7',
    'intuition>=0.4.2'
]


def long_description():
    try:
        with open('README.md') as f:
            return f.read()
    except IOError:
        return "failed to read README.md"

setup(
    name='insights',
    version=__version__,
    description=('Quantitative algorithms, portfolio managers, '
                 'data sources and contexts for Intuition'),
    author=__author__,
    author_email='xavier.bruhiere@gmail.com',
    packages=find_packages(),
    long_description=long_description(),
    license=__licence__,
    install_requires=requires,
    url="https://github.com/hackliff/insights",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Office/Business :: Financial',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Distributed Computing',
    ],
    scripts=['scripts/intuition-db'],
    data_files=[
        (os.path.expanduser('~/.intuition/R'), glob('./R/*')),
        (os.path.expanduser('~/.intuition/assets'), glob('./assets/*'))
    ])
