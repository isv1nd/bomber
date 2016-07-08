#!/usr/bin/env python
import os

from setuptools import setup, find_packages


REQUIREMENTS = 'requirements.txt'
TEST_REQUIREMENTS = 'test-requirements.txt'


def read_dependencies(filenames):
    dependencies = []
    for filename in filenames:
        with open(filename) as f:
            for line in f.readlines():
                if not line or line.startswith('#'):
                    continue
                dependencies.append(line.strip())
    return dependencies


setup(
    name='bomber',
    version='0.1',
    author='isv1nd',
    author_email='a.mishin@itransition.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=read_dependencies([REQUIREMENTS, TEST_REQUIREMENTS]),
    dependency_links=[],
)
