# coding: utf-8
from setuptools import setup

setup(
    name="apispec_serpyco",
    version="0.9",
    author="Algoo",
    author_email="contact@algoo.fr",
    description="Serpyco plugin for Apispec",
    license="MIT",
    keywords="apispec openapi serpyco api",
    url="https://github.com/algoo/apispec_plugins",
    packages=["apispec_serpyco"],
    long_description="https://github.com/algoo/apispec_plugins/tree/master/apispec_serpyco",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["apispec>=1.0.0b1", "serpyco>=0.16.1"],
    extras_require={"test": ["pytest"]},
)
