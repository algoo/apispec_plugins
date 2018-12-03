# coding: utf-8
from apispec.exceptions import APISpecError
from apispec.ext.marshmallow import OpenAPIConverter

from apispec_marshmallow_advanced.common import schema_class_resolver


class HapicOpenAPIConverter(OpenAPIConverter):
    def resolve_nested_schema(self, schema):
        """Method to resolve a dictinary from schemas

        Tests to see if the schema is already in the spec and adds it if
        necessary

        Typically will return a dictionary with the reference to the schema's
        path in the spec unless the `schema_name_resolver` returns `None` in
        which case the returned dictoinary will contain the schema's paramaters
        nested in place

        :param schema: schema to add to the spec
        """
        # CHANGED LINE HERE (use our schema_class_resolver)
        schema_cls = schema_class_resolver(self.spec, schema)
        name = self.schema_name_resolver(schema_cls)

        if not name:
            try:
                return self.schema2jsonschema(schema)
            except RuntimeError:
                raise APISpecError(
                    "Name resolver returned None for schema {schema} which is "
                    "part of a chain of circular referencing schemas. Please"
                    " ensure that the schema_name_resolver passed to"
                    " MarshmallowPlugin returns a string for all circular"
                    " referencing schemas.".format(schema=schema)
                )

        if schema_cls not in self.refs:
            self.spec.components.schema(
                name,
                # CHANGED LINE HERE (use schema_cls instead schema)
                schema=schema_cls,
            )
        return self.get_ref_dict(schema, schema_cls)
