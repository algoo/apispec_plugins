# coding: utf-8
from apispec.ext.marshmallow import OpenAPIConverter

from apispec_marshmallow_advanced.common import schema_class_resolver


class HapicOpenAPIConverter(OpenAPIConverter):
    def resolve_schema_class(self, schema):
        """See parent method"""
        return schema_class_resolver(self.spec, schema)
