apispec HapicMarshmallowPlugin
---------------------

`HapicMarshmallowPlugin` a simple overloading of
original apispec marshmallow plugin :

- manage `only` and `exclude` schema parameters and auto-generate associated schemas.
- works with auto-referencing mechanism

Install
-------

    pip install apispec_hapic_marshmallow

Tests
-----

To execute tests, be sure to install test tools

    pip install -e ".[test]"

To execute tests, run

    pytest tests
