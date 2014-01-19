#!/usr/bin/env python
#
# Copyright 2014 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
#import codecs
from glob import glob
from setuptools import setup, find_packages

from insights import __version__, __author__, __licence__


requires = [
    'numpy',
    'python-etcd',
    'pandas>=0.13.0.dev',
    'patsy',
    'redis',
    'rpy2',
    'pymongo',
    'PyYAML',
    'requests',
    'rethinkdb',
    'influxdb']


def long_description():
    try:
        #with codecs.open(readme, encoding='utf8') as f:
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
    data_files=[(os.path.expanduser('~/.intuition/R'), glob('./R/*'))],
    dependency_links=[
        'http://github.com/pydata/pandas/tarball/master#egg=pandas-0.13.0.dev']
)
