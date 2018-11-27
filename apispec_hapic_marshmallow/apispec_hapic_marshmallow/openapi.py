# coding: utf-8
from apispec.ext.marshmallow import OpenAPIConverter
import marshmallow

from apispec_hapic_marshmallow import schema_class_resolver


class HapicOpenAPIConverter(OpenAPIConverter):
    def __init__(self, openapi_version, spec):
        super().__init__(openapi_version)
        self.spec = spec

    def resolve_schema_dict(self, schema, dump=True, load=True, use_instances=False):
        """
        FIXME BS 2018-10-26: This is a complete copy-paste to permit usage of
        schema_class_resolver. Make a PR to make this method more overload
        friend.
        """
        if isinstance(schema, dict):
            if schema.get('type') == 'array' and 'items' in schema:
                schema['items'] = self.resolve_schema_dict(
                    schema['items'], use_instances=use_instances,
                )
            if schema.get('type') == 'object' and 'properties' in schema:
                schema['properties'] = {
                    k: self.resolve_schema_dict(v, dump=dump, load=load, use_instances=use_instances)
                    for k, v in schema['properties'].items()
                }
            return schema
        if isinstance(schema, marshmallow.Schema) and use_instances:
            schema_cls = schema
        else:
            # THIS IS THE CHANGED LINE
            # schema_cls = resolve_schema_cls(schema)
            schema_cls = schema_class_resolver(self.spec, schema)

        if schema_cls in self.refs:
            ref_path = self.get_ref_path()
            ref_schema = {'$ref': '#/{0}/{1}'.format(ref_path, self.refs[schema_cls])}
            if getattr(schema, 'many', False):
                return {
                    'type': 'array',
                    'items': ref_schema,
                }
            return ref_schema
        if not isinstance(schema, marshmallow.Schema):
            schema = schema_cls
        return self.schema2jsonschema(schema, dump=dump, load=load)
