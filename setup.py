#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.markdown') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

setup_requirements = [
    # TODO(drummonds): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

# TODO copy version from __init__ or vice versa can also do author and author email
setup(
    name='fab-support',
    version='0.1.6',
    description="Implement staging in Fabric and recipes for pelican to [local, s3] and Django to Heroku.",
    long_description=readme + '\n\n' + history,

    author="Humphrey Drummond",
    author_email='hum3@drummond.info',
    url='https://github.com/drummonds/fab_support',
    packages=find_packages(include=['fab_support']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='fab-support',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    entry_points={
        'console_scripts': ['fab-support=fab_support.command_line:main'],
    }
)
