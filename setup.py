#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="video_utils",
    version="1.1.0",
    author="Justin Dray",
    author_email="justin@dray.be",
    url="https://github.com/justin8/tv_report",
    description="This library is used for lots of shared functionality around parsing TV shows and movies.",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "colorama",
        "pymediainfo",
        "tqdm",
        "ffmpy",
    ],
    tests_require=["nose",
        "coverage",
        "mock",
    ],
    test_suite="nose.collector",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
    ],
)
