# coding: utf-8
from apispec.ext.marshmallow import OpenAPIConverter

from apispec_hapic_marshmallow.common import schema_class_resolver


class HapicOpenAPIConverter(OpenAPIConverter):
    def __init__(self, openapi_version, spec):
        super().__init__(openapi_version)
        self.spec = spec

    def resolve_schema_cls(self, schema):
        """Return schema class for given schema (instance or class)

        :param type|Schema|str: instance, class or class name of marshmallow.Schema
        :return: schema class of given schema (instance or class)
        """
        return schema_class_resolver(self.spec, schema)
