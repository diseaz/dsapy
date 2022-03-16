#!/usr/bin/python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="diseaz-dsapy",
    version="0.0.4",
    author="Dmitry Azhichakov",
    author_email="dazhichakov@gmail.com",
    description="Simple basic framework for command-line tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diseaz/dsapy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
