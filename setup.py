#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0',
                'lxml',
                'rpc-qtest-swagger-client<10.0.0',
                'requests',
                'future']
packages = ['zigzag']
entry_points = {
    'console_scripts': [
        'zigzag=zigzag.cli:main',
    ],
}

setup(
    name='rpc-zigzag',
    version='0.11.2',
    author="rcbops",
    author_email='rcb-deploy@lists.rackspace.com',
    maintainer='rcbops',
    maintainer_email='rcb-deploy@lists.rackspace.com',
    license="Apache Software License 2.0",
    url='https://github.com/rcbops/zigzag',
    keywords='zigzag',
    description="Parse JUnitXML and upload test results to qTest Manager.",
    long_description=readme + '\n\n' + history,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
    install_requires=requirements,
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    entry_points=entry_points,
)
