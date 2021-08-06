#!/usr/bin/env python
import os
from setuptools import setup, find_packages

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths
    
    
extra_files = package_files('oscar_lib/static')

setup(
    name='oscar_lib',
    version=0.80,
    description='library implementing some functions to interact with OSCAR/Surface',
    author='Timo Proescholdt',
    author_email='tproescholdt@wmo.int',
    url='https://github.com/kurt-hectic/oscar-client',
    packages=find_packages(),
    install_requires=[
        'setuptools',  'bs4', 'jsonpath_ng' , 'requests' , 'lxml' , 'jsonschema','xmltodict', 'strict-rfc3339', 'dict2xml' ,  'isodate'   
    ],
    tests_require=['xmldiff','python-dotenv'],
    package_data={'': extra_files},
)
