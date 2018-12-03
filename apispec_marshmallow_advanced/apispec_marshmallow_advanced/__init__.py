# coding: utf-8
from apispec.ext.marshmallow import MarshmallowPlugin

from apispec_marshmallow_advanced.common import generate_schema_name
from apispec_marshmallow_advanced.openapi import HapicOpenAPIConverter


class MarshmallowAdvancedPlugin(MarshmallowPlugin):
    def __init__(self, schema_name_resolver=None):
        schema_name_resolver = schema_name_resolver or generate_schema_name
        super().__init__(schema_name_resolver)

    def init_spec(self, spec):
        super().init_spec(spec)
        self.openapi = HapicOpenAPIConverter(
            openapi_version=spec.openapi_version,
            spec=self.spec,
            schema_name_resolver=self.schema_name_resolver,
        )
