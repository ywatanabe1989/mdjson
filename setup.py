#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-01 19:27:02 (ywatanabe)"
# File: /home/ywatanabe/proj/mdjson/setup.py

__file__ = "/home/ywatanabe/proj/mdjson/setup.py"

from setuptools import setup, find_packages

setup(
    name="mdjson",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandoc",
    ],
    python_requires=">=3.6",
    description="Convert between Markdown and simplified JSON format",
    author="Yusuke Watanabe",
    author_email="ywatanabe@alumni.u-tokyo.ac.jp",
    url="https://github.com/ywatanabe1989/mdjson",
    entry_points={
        'console_scripts': [
            'mdjson=mdjson.cli:main',
        ],
    }
)
