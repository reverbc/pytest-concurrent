#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-concurrent',
    version='0.2.0',
    author='James Wang, Reverb Chu',
    author_email='jamesw96@uw.edu, reverbc@me.com',
    maintainer='James Wang, Reverb Chu',
    maintainer_email='jamesw96@uw.edu, reverbc@me.com',
    license='MIT',
    url='https://github.com/reverbc/pytest-concurrent',
    description='Concurrently execute test cases with multithread'
                ', multiprocess and gevent',
    long_description=read('README.rst'),
    packages=['pytest_concurrent', 'pytest_concurrent.modes'],
    install_requires=[
        'pytest>=3.1.1',
        'futures;python_version<"3.0"',
        'psutil>=5.2.2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'concurrent = pytest_concurrent.plugin',
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
