# -*- coding: utf-8 -*-
import typing

from apispec.utils import OpenAPIVersion
import serpyco
from serpyco.schema import default_get_definition_name

import dataclasses

__location_map__ = {
    "query": "query",
    "querystring": "query",
    "json": "body",
    "headers": "header",
    "cookies": "cookie",
    "form": "formData",
    "files": "formData",
}


class OpenAPIConverter(object):
    """Converter generating OpenAPI specification from serpyco schemas and fields

    :param str|OpenAPIVersion openapi_version: The OpenAPI version to use.
        Should be in the form '2.x' or '3.x.x' to comply with the OpenAPI standard.
    """

    def __init__(
        self, openapi_version, schema_name_resolver=default_get_definition_name
    ):
        self.openapi_version = OpenAPIVersion(openapi_version)
        # Schema references
        self.refs = {}
        self._schema_name_resolver = schema_name_resolver

    def get_ref_path(self):
        """Return the path for references based on the openapi version"""
        ref_paths = {2: "definitions", 3: "components/schemas"}
        return ref_paths[self.openapi_version.major]

    def schema2jsonschema(self, schema, **kwargs):
        return self.fields2jsonschema(dataclasses.fields(schema), schema, **kwargs)

    def resolve_schema_dict(self, schema):
        if isinstance(schema, dict):
            if schema.get("type") == "array" and "items" in schema:
                schema["items"] = self.resolve_schema_dict(schema["items"])
            if schema.get("type") == "object" and "properties" in schema:
                schema["properties"] = {
                    k: self.resolve_schema_dict(v)
                    for k, v in schema["properties"].items()
                }
            return schema

        if schema in self.refs:
            ref_path = self.get_ref_path()
            ref_schema = {"$ref": "#/{0}/{1}".format(ref_path, self.refs[schema])}
            return ref_schema

        return self.schema2jsonschema(schema)

    def fields2jsonschema(self, fields, schema=None):
        """Convert dataclass field into json_schema"""
        field_names = [field.name for field in fields]
        serializer = serpyco.SchemaBuilder(
            dataclass=schema,
            only=field_names,
            get_definition_name=self._schema_name_resolver,
        )

        return serializer.json_schema()

    def schema2parameters(self, schema, **kwargs):
        """Return an array of OpenAPI parameters given a given dataclass.
        If `default_in` is "body", then return an array
        of a single parameter; else return an array of a parameter for each included field in
        the dataclass.

        https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#parameterObject
        """
        return self.fields2parameters(dataclasses.fields(schema), schema, **kwargs)

    def fields2parameters(
        self,
        fields,
        schema,
        default_in="body",
        name="body",
        required=False,
        description=None,
        **kwargs
    ):
        """Convert dataclass fields into OpenAPI parameters"""
        openapi_default_in = __location_map__.get(default_in, default_in)
        if self.openapi_version.major < 3 and openapi_default_in == "body":
            prop = self.resolve_schema_dict(schema)

            param = {
                "in": openapi_default_in,
                "required": required,
                "name": name,
                "schema": prop,
            }

            if description:
                param["description"] = description

            return [param]

        parameters = []
        body_param = None
        for field in fields:

            field_name = field.name
            field_obj = field

            param = self.field2parameter(
                schema, field_obj, name=field_name, default_in=default_in
            )
            if (
                self.openapi_version.major < 3
                and param["in"] == "body"
                and body_param is not None
            ):
                body_param["schema"]["properties"].update(param["schema"]["properties"])
                required_fields = param["schema"].get("required", [])
                if required_fields:
                    body_param["schema"].setdefault("required", []).extend(
                        required_fields
                    )
            else:
                if self.openapi_version.major < 3 and param["in"] == "body":
                    body_param = param
                parameters.append(param)
        return parameters

    def field2parameter(self, schema, field, name="body", default_in="body"):
        """Return an OpenAPI parameter as a `dict`, given a dataclass field.

        https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#parameterObject
        """
        assert schema

        serializer = serpyco.SchemaBuilder(
            schema, only=[field.name], get_definition_name=self._schema_name_resolver
        )
        field_json_schema = serializer.json_schema()["properties"][field.name]

        return self.property2parameter(
            field_json_schema,
            name=name,
            required=isinstance(field.default, dataclasses._MISSING_TYPE),
            multiple=isinstance(field.type, typing.Sequence),
            default_in=default_in,
        )

    def property2parameter(
        self,
        prop,
        name="body",
        required=False,
        multiple=False,
        location=None,
        default_in="body",
    ):
        """Return the Parameter Object definition for a JSON Schema property.

        https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#parameterObject

        :param dict prop: JSON Schema property
        :param str name: Field name
        :param bool required: Parameter is required
        :param bool multiple: Parameter is repeated
        :param str location: Location to look for ``name``
        :param str default_in: Default location to look for ``name``
        :raise: TranslationError if arg object cannot be translated to a Parameter Object schema.
        :rtype: dict, a Parameter Object
        """
        openapi_default_in = __location_map__.get(default_in, default_in)
        openapi_location = __location_map__.get(location, openapi_default_in)
        ret = {"in": openapi_location, "name": name}

        if openapi_location == "body":
            ret["required"] = False
            ret["name"] = "body"
            ret["schema"] = {
                "type": "object",
                "properties": {name: prop} if name else {},
            }
            if name and required:
                ret["schema"]["required"] = [name]
        else:
            ret["required"] = required
            if self.openapi_version.major < 3:
                if multiple:
                    ret["collectionFormat"] = "multi"
                ret.update(prop)
            else:
                if multiple:
                    ret["explode"] = True
                    ret["style"] = "form"
                if prop.get("description", None):
                    ret["description"] = prop.pop("description")
                ret["schema"] = prop
        return ret
