import os

from setuptools import find_packages
from setuptools import setup
import sys




setup(
    name='linkat',
    version='0.0.3',
    description='Linkat',
    author="Antoine Blaud",
    author_email="antoine.blaud@gmail.com",
    setup_requires=['setuptools'],
    py_modules=['linkat'],
    entry_points={
        'console_scripts': [ 'linkat-run = linkat.linkat:main' ]
    },
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-Cors',
        'pyparsing',
        'tqdm',
    ]
)    