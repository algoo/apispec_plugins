# coding: utf-8
import typing

from apispec.ext.marshmallow import MarshmallowPlugin

from apispec_hapic_marshmallow.openapi import HapicOpenAPIConverter


class HapicMarshmallowPlugin(MarshmallowPlugin):
    def __init__(self, schema_name_resolver=None):
        super().__init__(schema_name_resolver=schema_name_resolver)
        self.openapi = None  # type: typing.Optional[HapicOpenAPIConverter]

    def init_spec(self, spec):
        super().init_spec(spec)
        self.openapi = HapicOpenAPIConverter(openapi_version=spec.openapi_version, spec=self.spec)
