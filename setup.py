#!/usr/bin/env python

from setuptools import setup, find_packages
import sys

setup(
    name='epicov_downloader',
    version= '20.12.14',
    author='Po-E Li',
    author_email='po-e@lanl.gov',
    packages=find_packages(),
    python_requires='>=3.6',
    scripts=['gisaid_EpiCoV_downloader.py'],
    url='https://github.com/poeli/EpiCoV_downloader',
    license='LICENSE',
    description='This is a GISAID downloader to retrieve EpiCoV sequences and the table.',
    keywords="gisaid, epicov, sars-cov-2, downloader",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "selenium"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)