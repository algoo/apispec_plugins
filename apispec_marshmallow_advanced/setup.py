# coding: utf-8
from setuptools import setup

setup(
    name="apispec_marshmallow_advanced",
    version="0.4",
    author="Algoo",
    author_email="contact@algoo.fr",
    description="Marshmallow apispec plugin for hapic",
    license="MIT",
    keywords="apispec openapi marshmallow api",
    url="https://github.com/algoo/apispec_plugins",
    packages=["apispec_marshmallow_advanced"],
    long_description="https://github.com/algoo/apispec_plugins/tree/master/apispec_marshmallow_advanced",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["apispec>=1.1.0,<3", "marshmallow"],
    extras_require={"test": ["pytest"]},
    data_files = [("", ["LICENSE"])],
)
