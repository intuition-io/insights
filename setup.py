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


import sys
import os
from glob import glob
from setuptools import setup, find_packages

from insights import __version__, __author__, __licence__


LONG_DESCRIPTION = None
README_MARKDOWN = None


def get_requirements():
    with open('./requirements.txt') as requirements:
        # Avoid github based requirements
        deps = requirements.read().split('\n')[:-1]
        deps.pop(1)
        deps.insert(1, 'pandas>=0.13.0.dev')
        return deps

with open('README.md') as markdown_source:
    README_MARKDOWN = markdown_source.read()

if 'upload' in sys.argv:
    # Converts the README.md file to ReST, since PyPI uses ReST for formatting,
    # This allows to have one canonical README file, being the README.md
    # The conversion only needs to be done on upload.
    # Otherwise, the pandoc import and errors that are thrown when
    # pandoc are both overhead and a source of confusion for general
    # usage/installation.
    import pandoc
    pandoc.core.PANDOC_PATH = '/usr/bin/pandoc'
    doc = pandoc.Document()
    doc.markdown = README_MARKDOWN
    LONG_DESCRIPTION = doc.rst
else:
    # If pandoc isn't installed, e.g. when downloading from pip,
    # just use the regular README.
    LONG_DESCRIPTION = README_MARKDOWN

setup(
    name='insights',
    version=__version__,
    description=('Quantitative algorithms, portfolio managers, '
                 'data sources and contexts for Intuition'),
    author=__author__,
    author_email='xavier.bruhiere@gmail.com',
    packages=find_packages(),
    long_description=LONG_DESCRIPTION,
    license=__licence__,
    install_requires=get_requirements(),
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
