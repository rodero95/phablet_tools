#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='phablet-tools',
    version='0.1',
    description='Scripts to deploy Ubuntu on mobile devices',
    author='Sergio Schvezov',
    author_email='sergio.schvezov@canonical.com',
    license='GPLv3',
    packages=find_packages(),
    scripts=['phablet-flash',
             'phablet-network-setup',
             'phablet-dev-bootstrap',
             'repo',
            ],
)
