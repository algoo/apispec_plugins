# coding: utf-8
from marshmallow import fields
from apispec.ext.marshmallow import MarshmallowPlugin

from apispec_hapic_marshmallow.common import schema_class_resolver
from apispec_hapic_marshmallow.openapi import HapicOpenAPIConverter


class HapicMarshmallowPlugin(MarshmallowPlugin):
    def init_spec(self, spec):
        super().init_spec(spec)
        self.openapi = HapicOpenAPIConverter(openapi_version=spec.openapi_version, spec=self.spec)

    def inspect_schema_for_auto_referencing(self, original_schema_instance):
        """Override of apispec.ext.marshmallow.MarshmallowPlugin to be able to
        use our schema_class_resolver (generate class with care of exclude/only)

        FIXME BS 2018-10-26: This is a complete copy-paste to permit usage of
        schema_class_resolver. Make a PR to make this method more overload
        friend.

        :param original_schema_instance: schema to parse
        """
        # schema_name_resolver must be provided to use this function
        assert self.schema_name_resolver

        for field in original_schema_instance.fields.values():
            nested_schema_class = None

            if isinstance(field, fields.Nested):
                # THIS IS THE CHANGED LINE
                # nested_schema_class = self.spec.schema_class_resolver(
                nested_schema_class = schema_class_resolver(
                    self.spec,
                    field.schema,
                )

            elif isinstance(field, fields.List) \
                    and isinstance(field.container, fields.Nested):
                # THIS IS THE CHANGED LINE
                # nested_schema_class = self.spec.schema_class_resolver(
                nested_schema_class = schema_class_resolver(
                    self.spec,
                    field.container.schema,
                )

            if nested_schema_class and nested_schema_class not in self.openapi.refs:
                definition_name = self.schema_name_resolver(
                    nested_schema_class,
                )
                if definition_name:
                    self.spec.components.schema(
                        definition_name,
                        schema=nested_schema_class,
                    )
