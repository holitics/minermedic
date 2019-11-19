#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io, os

from setuptools import find_packages, setup
from setup_functions import get_package_version, get_package_requirements

# Package meta-data.
NAME = 'minermedic'
DESCRIPTION = 'MinerMedic'
URL = 'https://github.com/holitics/minermedic'
EMAIL = 'nick.saparoff@gmail.com'
AUTHOR = 'Holitics'
REQUIRES_PYTHON = '>=3.6.0'
SOURCE_DIRECTORY = 'phenome'

# get the root dir
rootdir = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(rootdir, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# get the build version
build_version = get_package_version(SOURCE_DIRECTORY, rootdir, True)

# get the package requirements from the requirements.txt file
REQUIRED = get_package_requirements()

print ("Required Libraries are:")
for lib in REQUIRED:
    print (lib)

setup(
    name=NAME,
    version=build_version,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["test", "*.test", "*.test.*", "test.*"]),
    install_requires=REQUIRED,
    extras_require={},
    include_package_data=False,
    license='Apache-2.0',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: System :: Networking :: Monitoring'
    ],

    cmdclass={
    },

)
