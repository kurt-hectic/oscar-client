#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='oscar_lib',
    version=0.22,
    description='library implementing some functions to interact with OSCAR/Surface',
    author='Timo Proescholdt',
    author_email='tproescholdt@wmo.int',
    url='https://github.com/kurt-hectic/oscar-lib',
    packages=find_packages(),
    install_requires=[
        'setuptools',  'bs4', 'jsonpath_ng' , 'requests' , 'lxml' , 'jsonschema','xmltodict', 'strict-rfc3339'   
    ],
)