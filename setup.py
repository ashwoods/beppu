#!/usr/bin/env python

"""
Beppu
=====

Provides a utility asyncio synchronization primitive based on `asyncio.Event`
and `enum.Enum`.

"""
from setuptools import setup, find_packages
from pathlib import Path

PARENT_DIR = Path(__file__).parent

test_deps = [
    "colorlog",
    "pytest",
    "pytest-cov",
    "pytest-flake8",
    "flake8-bugbear",
    "flake8-import-order",
    "pytest-black",
    "pytest-asyncio",
    "pytest-bandit",
    "pytest-benchmark",
    "pytest-profiling",
    "pytest-leaks",
    "memory_profiler",
    "pytest-xdist",
    "pdbpp",
]
extras = {
    "test": test_deps,
}

setup(
    name="beppu",
    version="0.0.1",
    author="Ashley Camba Garrido",
    author_email="ashwoods@gmail.com",
    url="https://github.com/ashwoods/beppu",
    description="Enum based asyncio synchronization event wrapper",
    long_description=__doc__,
    packages=find_packages(exclude=("tests", "tests.*")),
    zip_safe=False,
    license="MIT",
    tests_require=test_deps,
    extras_require=extras,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
