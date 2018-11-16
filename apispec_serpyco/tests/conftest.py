# -*- coding: utf-8 -*-
from collections import namedtuple

import pytest

from apispec import APISpec
from apispec_serpyco import SerpycoPlugin


def make_spec(openapi_version):
    s_plugin = SerpycoPlugin()
    spec = APISpec(
        title='Validation',
        version='0.1',
        openapi_version=openapi_version,
        plugins=(s_plugin, ),
    )
    return namedtuple(
        'Spec', ('spec', 'serpyco_plugin', 'openapi'),
    )(
        spec, s_plugin, s_plugin.openapi,
    )


@pytest.fixture(params=('2.0', '3.0.0'))
def spec_fixture(request):
    return make_spec(request.param)


@pytest.fixture(params=('2.0', '3.0.0'))
def spec(request):
    return make_spec(request.param).spec
