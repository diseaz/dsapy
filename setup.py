#!/usr/bin/python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="diseaz-base-py-framework",
    version="0.0.1",
    author="Dmitry Azhichakov",
    author_email="diseaz@github.com",
    description="Simple basic command-line tool framework",
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
