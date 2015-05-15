#!/usr/bin/env python3

import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]
    
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []
        
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
        
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name = 'pycoin',
    packages = ['pycoin'],
    install_requires = [
        'tmdbsimple==1.3.0',
        'requests==2.5.3'
    ],
    tests_require = [
        'pytest',
        'pytest-cov',
        'pytest-mock'
    ],
    cmdclass = {'test': PyTest}
)
