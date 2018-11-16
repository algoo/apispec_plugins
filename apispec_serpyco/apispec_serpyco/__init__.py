# -*- coding: utf-8 -*-
"""Serpyco plugin for apispec. Allows passing a python dataclass
to `APISpec.definition <apispec.APISpec.definition>`
and `APISpec.path <apispec.APISpec.path>` (for responses). Note serpyco field type is supported.
"""
from apispec import BasePlugin
from apispec_serpyco.openapi import OpenAPIConverter

import serpyco


def extract_definition_from_json_schema(definition):
    definitions = {}

    for name, definition in definition.get('definitions', {}).items():
        definitions[name] = definition
        if definition.get('definitions'):
            definitions.update(extract_definition_from_json_schema(definition))

    return definitions


def replace_refs_for_openapi3(data):
    for key, value in data.items():
        if isinstance(value, dict):
            replace_refs_for_openapi3(value)
        elif key == '$ref' and value.startswith('#/definitions'):
            data[key] = value.replace('#/definitions', '#/components/schemas')


def replace_auto_refs(schema_name, data, openapi_version):
    for key, value in data.items():
        if isinstance(value, dict):
            replace_auto_refs(schema_name, value, openapi_version)
        elif key == '$ref' and value == '#':
            if openapi_version.major < 3:
                data[key] = '#/definitions/{}'.format(schema_name)
            else:
                data[key] = '#/components/schemas/{}'.format(schema_name)


class SerpycoPlugin(BasePlugin):
    """APISpec plugin handling python dataclass (with serpyco typing support)"""

    def __init__(self):
        super(SerpycoPlugin, self).__init__()
        self.spec = None
        # self.schema_name_resolver = schema_name_resolver
        self.openapi_version = None
        self.openapi = None

    def init_spec(self, spec):
        """Initialize plugin with APISpec object

        :param APISpec spec: APISpec object this plugin instance is attached to
        """
        super(SerpycoPlugin, self).init_spec(spec)
        self.spec = spec
        self.openapi_version = spec.openapi_version
        self.openapi = OpenAPIConverter(openapi_version=spec.openapi_version)

    def schema_helper(self, name, schema=None, **kwargs):
        """Definition helper that allows using a dataclass to provide
        OpenAPI metadata.

        :param type|type schema a dataclass class
        """
        with_definition = kwargs.get('with_definition')

        if schema is None and not with_definition:
            return None

        if with_definition:
            return with_definition

        # Store registered refs, keyed by Schema class
        self.openapi.refs[schema] = name

        serializer = serpyco.Serializer(schema)
        json_schema = serializer.json_schema()

        # TODO BS 2018-10-15: Must parse json_schema to update $ref into OpenAPI
        # compatible version
        if self.openapi_version.major > 2:
            replace_refs_for_openapi3(json_schema['properties'])

        # Replace auto reference to absolute reference
        replace_auto_refs(name, json_schema['properties'], self.openapi_version)

        # If definitions in json_schema, add them
        if json_schema.get('definitions'):
            # FIXME BS 2018-10-16: There is a problematic here: the serializer produce ref with an
            # automatic naming. This naming is used here but with apispec usage, name can be
            # different because specified in name parameter.
            flat_definitions = extract_definition_from_json_schema(json_schema)
            for name, definition in flat_definitions.items():
                self.spec.components.schema(
                    name,
                    with_definition=definition,
                )

        json_schema.pop('definitions', None)

        return json_schema

    def parameter_helper(self, **kwargs):
        """Parameter component helper that allows using a dataclass
        in parameter definition.

        :param type|type schema: A dataclass.
        """
        # In OpenAPIv3, this only works when using the complex form using "content"
        self.resolve_schema(kwargs)
        return kwargs

    def response_helper(self, **kwargs):
        """Response component helper that allows using a dataclass in response definition.

        :param type|Schema schema: A marshmallow Schema class or instance.
        """
        self.resolve_schema(kwargs)
        return kwargs

    def operation_helper(self, path=None, operations=None, **kwargs):
        """May mutate operations.

        :param str path: Path to the resource
        :param dict operations: A `dict` mapping HTTP methods to operation object.
        """
        for operation in operations.values():
            if not isinstance(operation, dict):
                continue
            if 'parameters' in operation:
                operation['parameters'] = self.resolve_parameters(operation['parameters'])
            if self.openapi_version.major >= 3:
                if 'requestBody' in operation:
                    self.resolve_schema_in_request_body(operation['requestBody'])
            for response in operation.get('responses', {}).values():
                self.resolve_schema(response)

    def resolve_schema_in_request_body(self, request_body):
        """Function to resolve a schema in a requestBody object - modifies then
        response dict to convert dataclass into dict
        """
        content = request_body['content']
        for content_type in content:
            schema = content[content_type]['schema']
            content[content_type]['schema'] = self.openapi.resolve_schema_dict(schema)

    def resolve_schema(self, data):
        """Function to resolve a schema in a parameter or response - modifies the
        corresponding dict to convert dataclass class into dict

        :param APISpec spec: `APISpec` containing refs.
        :param dict data: the parameter or response dictionary that may contain a dataclass
        :param bool dump: Introspect dump logic.
        :param bool load: Introspect load logic.
        """
        if self.openapi_version.major < 3:
            if 'schema' in data:
                data['schema'] = self.openapi.resolve_schema_dict(data['schema'])
        else:
            if 'content' in data:
                for content_type in data['content']:
                    schema = data['content'][content_type]['schema']
                    data['content'][content_type]['schema'] = self.openapi.resolve_schema_dict(
                        schema
                    )

    def resolve_parameters(self, parameters):
        resolved = []
        for parameter in parameters:
            if not isinstance(parameter.get('schema', {}), dict):
                schema = parameter['schema']
                if 'in' in parameter:
                    del parameter['schema']
                    resolved += self.openapi.schema2parameters(
                        schema,
                        default_in=parameter.pop('in'), **parameter
                    )
                    continue
            self.resolve_schema(parameter)
            resolved.append(parameter)
        return resolved
