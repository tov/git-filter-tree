#!/usr/bin/env python3
from setuptools import setup

long_description = None

setup(
    name='git-filter-tree',
    version='0.0.0',
    description='Efficient tree filtering (examples)',
    long_description=long_description,
    author='Thomas Gläßle',
    author_email='thomas@coldfix.de',
    url='https://github.com/coldfix/git-filter-tree',
    license='GPLv3',
    packages=['git_filter_tree'],
    entry_points = {
        'console_scripts': [
            'git-filter-tree = git_filter_tree.__main__:main',
        ],
    },
    install_requires=[],
    classifiers= [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Version Control :: Git',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
)