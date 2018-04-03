#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

dependency_links = ['http://github.com/ryan-rs/qtest-swagger-client/tarball/master#egg=swagger-client-1.0.0']
requirements = ['Click>=6.0', 'swagger-client', 'lxml']
setup_requirements = ['pytest-runner']

setup(
    author="rcbops",
    author_email='rcb-deploy@lists.rackspace.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Parse JUnitXML and upload test results to qTest Manager.",
    dependency_links=dependency_links,
    entry_points={
        'console_scripts': [
            'zigzag=zigzag.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='zigzag',
    name='zigzag',
    packages=find_packages(include=['zigzag']),
    setup_requires=setup_requirements,
    url='https://github.com/rcbops/zigzag',
    version='0.5.0',
    zip_safe=False,
)
