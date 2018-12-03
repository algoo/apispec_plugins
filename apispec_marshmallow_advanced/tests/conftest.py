# coding: utf-8
from collections import namedtuple

from apispec import APISpec
import pytest

from apispec_marshmallow_advanced import MarshmallowAdvancedPlugin
from apispec_marshmallow_advanced.common import generate_schema_name


def make_spec(openapi_version):
    m_plugin = MarshmallowAdvancedPlugin(schema_name_resolver=generate_schema_name)
    spec = APISpec(
        title="Validation",
        version="0.1",
        openapi_version=openapi_version,
        plugins=(m_plugin,),
    )
    return namedtuple("Spec", ("spec", "marshmallow_plugin", "openapi"))(
        spec, m_plugin, m_plugin.openapi
    )


@pytest.fixture(params=("2.0", "3.0.0"))
def spec_fixture(request):
    return make_spec(request.param)


@pytest.fixture(params=("2.0", "3.0.0"))
def spec(request):
    return make_spec(request.param).spec
