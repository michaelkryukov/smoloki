# -*- coding: utf-8 -*-

import os
import setuptools


assert os.environ.get("GITHUB_REF_TYPE") == "tag"
assert os.environ.get("GITHUB_REF_NAME")
VERSION = os.environ["GITHUB_REF_NAME"]


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="smoloki",
    version=VERSION,
    author="Michael Krukov",
    author_email="krukov.michael@ya.ru",
    keywords=["library", "loki"],
    description="Tiny library to push logs to `Grafana Loki` in `logfmt` format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michaelkryukov/smoloki",
    packages=setuptools.find_packages(include=("smoloki",)),
    install_requires=[
        "aiohttp~=3.8.3",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
)
