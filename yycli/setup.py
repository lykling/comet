#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""yycli setup
"""
# import pkg_resources
# import importlib.resources
from setuptools import setup
# install_requires = pkg_resources.resource_string(
#     __name__,
#     'requirements.txt').splitlines()
with open('requirements.txt', 'rb') as f:
    install_requires = f.read().splitlines()
# install_requires = importlib.resources.read_text(
#     '', 'requirements.txt').splitlines()
print('install_requires:', install_requires)

__version__ = '0.0.1'

setup(
    name='yycli',
    version=__version__,
    description='tools for daily work',
    author='Pride Leong',
    author_email='lykling.lyk@gmail.com',
    package_dir={'yycli': '.'},
    packages=[
        'yycli',
        'yycli.commands',
    ],
    package_data={
        'yycli': ['requirements.txt', 'conf/*', 'conf/**/*'],
    },
    entry_points={
        'console_scripts': ['yy = yycli.__main__:main'],
    },
    install_requires=[x.decode() for x in install_requires],
    # script_name='./yycli/setup.py',
    # data_files=[('yycli', ['./yycli/setup.py'])]
)
