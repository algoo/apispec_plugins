# -*- coding: utf-8 -*-
import dataclasses
import serpyco
import typing
from dataclasses import dataclass

import pytest

from apispec import APISpec
from apispec_serpyco import SerpycoPlugin
from tests.utils import ref_path
from tests.utils import get_definitions
from tests.utils import get_parameters
from tests.utils import get_responses
from tests.utils import get_paths


@dataclass
class PetSchema(object):
    # TODO BS 2018-10-13: Manage dump only and load_only ?
    id: int
    name: str
    # password = fields.Str(load_only=True, description=description['password'])
    password: str


@dataclass
class SampleSchema(object):
    # TODO BS 2018-10-14: exclude ?
    # runs = fields.Nested('RunSchema', many=True, exclude=('sample',))
    runs: typing.List['RunSchema']
    count: int


@dataclass
class RunSchema(object):
    # TODO BS 2018-10-14: exclude ?
    # sample = fields.Nested(SampleSchema, exclude=('runs',))
    sample: typing.List[SampleSchema]


@dataclass
class AnalysisSchema(object):
    sample: SampleSchema


@dataclass
class AnalysisWithListSchema(object):
    samples: typing.List[SampleSchema]


@dataclass
class SelfReferencingSchema(object):
    id: int
    single: 'SelfReferencingSchema'
    many: typing.List['SelfReferencingSchema']


@dataclass
class DefaultValuesSchema(object):
    number_auto_default: int = dataclasses.field(default=12)
    string_callable_default: str = dataclasses.field(default_factory=lambda: 'Callable')
    numbers: typing.List[int] = dataclasses.field(default_factory=lambda: [])


class TestDefinitionHelper:

    @pytest.mark.parametrize('schema', [PetSchema])
    def test_can_use_schema_as_definition(self, spec, schema):
        spec.components.schema('Pet', schema=schema)
        definitions = get_definitions(spec)
        props = definitions['Pet']['properties']

        assert props['id']['type'] == 'integer'
        assert props['name']['type'] == 'string'

    def test_schema_helper_without_schema(self, spec):
        spec.components.schema('Pet', properties={'key': {'type': 'integer'}})
        definitions = get_definitions(spec)
        assert definitions['Pet']['properties'] == {'key': {'type': 'integer'}}

    @pytest.mark.parametrize('schema', [AnalysisSchema])
    def test_resolve_schema_dict_auto_reference(self, schema):
        def resolver(schema):
            return schema.__name__
        spec = APISpec(
            title='Test auto-reference',
            version='0.1',
            openapi_version='2.0',
            plugins=(
                # SerpycoPlugin(schema_name_resolver=resolver),
                SerpycoPlugin(),
            ),
        )
        assert {} == get_definitions(spec)

        spec.components.schema('analysis', schema=schema)
        spec.path(
            '/test', operations={
                'get': {
                    'responses': {
                        '200': {
                            'schema': {
                                '$ref': '#/definitions/analysis',
                            },
                        },
                    },
                },
            },
        )
        definitions = get_definitions(spec)
        assert 3 == len(definitions)

        assert 'analysis' in definitions
        assert 'SampleSchema' in definitions
        assert 'RunSchema' in definitions

    @pytest.mark.parametrize('schema', [AnalysisWithListSchema])
    def test_resolve_schema_dict_auto_reference_in_list(self, schema):
        def resolver(schema):
            return schema.__name__
        spec = APISpec(
            title='Test auto-reference',
            version='0.1',
            openapi_version='2.0',
            plugins=(
                SerpycoPlugin(),
            ),
        )
        assert {} == get_definitions(spec)

        spec.components.schema('analysis', schema=schema)
        spec.path(
            '/test', operations={
                'get': {
                    'responses': {
                        '200': {
                            'schema': {
                                '$ref': '#/definitions/analysis',
                            },
                        },
                    },
                },
            },
        )
        definitions = get_definitions(spec)
        assert 3 == len(definitions)

        assert 'analysis' in definitions
        assert 'SampleSchema' in definitions
        assert 'RunSchema' in definitions


class TestComponentParameterHelper(object):

    @pytest.mark.parametrize('schema', [PetSchema])
    def test_can_use_schema_in_parameter(self, spec, schema):
        if spec.openapi_version.major < 3:
            kwargs = {'schema': schema}
        else:
            kwargs = {'content': {'application/json': {'schema': schema}}}
        spec.components.parameter('Pet', 'body', **kwargs)
        parameter = get_parameters(spec)['Pet']
        assert parameter['in'] == 'body'
        if spec.openapi_version.major < 3:
            schema = parameter['schema']['properties']
        else:
            schema = parameter['content']['application/json']['schema']['properties']

        assert schema['name']['type'] == 'string'
        assert schema['password']['type'] == 'string'
        # dump_only field is ignored
        # FIXME BS 2018-10-15: implement dump_only
        # assert 'id' not in schema


class TestComponentResponseHelper:

    @pytest.mark.parametrize('schema', [PetSchema])
    def test_can_use_schema_in_response(self, spec, schema):
        if spec.openapi_version.major < 3:
            kwargs = {'schema': schema}
        else:
            kwargs = {'content': {'application/json': {'schema': schema}}}
        spec.components.response('GetPetOk', **kwargs)
        response = get_responses(spec)['GetPetOk']
        if spec.openapi_version.major < 3:
            schema = response['schema']['properties']
        else:
            schema = response['content']['application/json']['schema']['properties']

        assert schema['id']['type'] == 'integer'
        assert schema['name']['type'] == 'string'
        # load_only field is ignored
        # FIXME BS 2018-10-15: implement dump_only
        # assert 'password' not in schema


class TestCustomField:

    def test_can_use_custom_field_decorator(self, spec_fixture):
        @dataclass
        class CustomPetASchema(PetSchema):
            email: str = serpyco.string_field(
                format_=serpyco.StringFormat.EMAIL,
                pattern="^[A-Z]",
                min_length=3,
                max_length=24,
            )

        @dataclass
        class CustomPetBSchema(PetSchema):
            age: int = serpyco.number_field(
                minimum=1,
                maximum=120,
            )

        @dataclass
        class WithStringField(object):
            """String field test class"""

            foo: str = serpyco.string_field(
                format_=serpyco.StringFormat.EMAIL,
                pattern="^[A-Z]",
                min_length=3,
                max_length=24,
            )

        serializer = serpyco.Serializer(WithStringField)
        serializer.json_schema()

        spec_fixture.spec.components.schema('Pet', schema=PetSchema)
        spec_fixture.spec.components.schema('CustomPetA', schema=CustomPetASchema)
        spec_fixture.spec.components.schema('CustomPetB', schema=CustomPetBSchema)

        props_0 = get_definitions(spec_fixture.spec)['Pet']['properties']
        props_a = get_definitions(spec_fixture.spec)['CustomPetA']['properties']
        props_b = get_definitions(spec_fixture.spec)['CustomPetB']['properties']

        assert props_0['name']['type'] == 'string'
        assert 'format' not in props_0['name']

        assert props_a['email']['type'] == 'string'
        # FIXME BS 2018-10-15: Is OpenApi valid ?!
        assert str(props_a['email']['format']) == 'StringFormat.EMAIL'
        assert props_a['email']['pattern'] == '^[A-Z]'
        assert props_a['email']['maxLength'] == 24
        assert props_a['email']['minLength'] == 3

        assert props_b['age']['type'] == 'integer'
        assert props_b['age']['minimum'] == 1
        assert props_b['age']['maximum'] == 120


class TestOperationHelper:

    @staticmethod
    def ref_path(spec):
        if spec.openapi_version.version[0] < 3:
            return '#/definitions/'
        return '#/components/schemas/'

    @pytest.mark.parametrize('pet_schema', (PetSchema, ))
    # TODO BS 2018-10-15: str schema ?
    # @pytest.mark.parametrize('pet_schema', (PetSchema, 'tests.schemas.PetSchema'))
    @pytest.mark.parametrize('spec_fixture', ('2.0', ), indirect=True)
    def test_schema_v2(self, spec_fixture, pet_schema):
        spec_fixture.spec.path(
            path='/pet',
            operations={
                'get': {
                    'responses': {
                        200: {
                            'schema': pet_schema,
                            'description': 'successful operation',
                        },
                    },
                },
            },
        )
        get = get_paths(spec_fixture.spec)['/pet']['get']
        assert get['responses'][200]['schema'] == spec_fixture.openapi.schema2jsonschema(
            PetSchema,
        )
        assert get['responses'][200]['description'] == 'successful operation'

    @pytest.mark.parametrize('pet_schema', (PetSchema, ))
    # TODO BS 2018-10-15: str schema ?
    # @pytest.mark.parametrize('pet_schema', (PetSchema, PetSchema(), 'tests.schemas.PetSchema'))
    @pytest.mark.parametrize('spec_fixture', ('3.0.0', ), indirect=True)
    def test_schema_v3(self, spec_fixture, pet_schema):
        spec_fixture.spec.path(
            path='/pet',
            operations={
                'get': {
                    'responses': {
                        200: {
                            'content': {
                                'application/json': {
                                    'schema': pet_schema,
                                },
                            },
                            'description': 'successful operation',
                        },
                    },
                },
            },
        )
        get = get_paths(spec_fixture.spec)['/pet']['get']
        resolved_schema = get['responses'][200]['content']['application/json']['schema']
        assert resolved_schema == spec_fixture.openapi.schema2jsonschema(
            PetSchema
        )
        assert get['responses'][200]['description'] == 'successful operation'

    @pytest.mark.parametrize('spec_fixture', ('2.0', ), indirect=True)
    def test_schema_expand_parameters_v2(self, spec_fixture):
        spec_fixture.spec.path(
            path='/pet',
            operations={
                'get': {
                    'parameters': [{
                        'in': 'query',
                        'schema': PetSchema,
                    }],
                },
                'post': {
                    'parameters': [{
                        'in': 'body',
                        'description': 'a pet schema',
                        'required': True,
                        'name': 'pet',
                        'schema': PetSchema,
                    }],
                },
            },
        )
        p = get_paths(spec_fixture.spec)['/pet']
        get = p['get']
        assert get['parameters'] == spec_fixture.openapi.schema2parameters(
            PetSchema, default_in='query',
        )
        post = p['post']
        assert post['parameters'] == spec_fixture.openapi.schema2parameters(
            PetSchema, default_in='body', required=True,
            name='pet', description='a pet schema',
        )

    @pytest.mark.parametrize('spec_fixture', ('3.0.0', ), indirect=True)
    def test_schema_expand_parameters_v3(self, spec_fixture):
        spec_fixture.spec.path(
            path='/pet',
            operations={
                'get': {
                    'parameters': [{
                        'in': 'query',
                        'schema': PetSchema,
                    }],
                },
                'post': {
                    'requestBody': {
                        'description': 'a pet schema',
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': PetSchema,
                            },
                        },
                    },
                },
            },
        )
        p = get_paths(spec_fixture.spec)['/pet']
        get = p['get']
        assert get['parameters'] == spec_fixture.openapi.schema2parameters(
            PetSchema, default_in='query',
        )
        # FIXME BS 2018-10-15: Must implement description in serpyco
        # for parameter in get['parameters']:
        #     description = parameter.get('description', False)
        #     assert description
        #     name = parameter['name']
        #     assert description == PetSchema.description[name]
        post = p['post']
        post_schema = spec_fixture.openapi.resolve_schema_dict(
            PetSchema
        )
        assert post['requestBody']['content']['application/json']['schema'] == post_schema
        assert post['requestBody']['description'] == 'a pet schema'
        assert post['requestBody']['required']

    @pytest.mark.parametrize('spec_fixture', ('2.0', ), indirect=True)
    def test_schema_uses_ref_if_available_v2(self, spec_fixture):
        spec_fixture.spec.components.schema('Pet', schema=PetSchema)
        spec_fixture.spec.path(
            path='/pet',
            operations={
                'get': {
                    'responses': {
                        200: {
                            'schema': PetSchema,
                        },
                    },
                },
            },
        )
        get = get_paths(spec_fixture.spec)['/pet']['get']
        assert get['responses'][200]['schema']['$ref'] == self.ref_path(
            spec_fixture.spec
        ) + 'Pet'

    @pytest.mark.parametrize('spec_fixture', ('3.0.0', ), indirect=True)
    def test_schema_uses_ref_if_available_v3(self, spec_fixture):
        spec_fixture.spec.components.schema('Pet', schema=PetSchema)
        spec_fixture.spec.path(
            path='/pet',
            operations={
                'get': {
                    'responses': {
                        200: {
                            'content': {
                                'application/json': {
                                    'schema': PetSchema,
                                },
                            },
                        },
                    },
                },
            },
        )
        get = get_paths(spec_fixture.spec)['/pet']['get']
        assert get['responses'][200]['content']['application/json']['schema']['$ref'] == self.ref_path(
            spec_fixture.spec,
        ) + 'Pet'

    @pytest.mark.parametrize('spec_fixture', ('2.0', ), indirect=True)
    def test_schema_uses_ref_in_parameters_and_request_body_if_available_v2(self, spec_fixture):
        spec_fixture.spec.components.schema('Pet', schema=PetSchema)
        spec_fixture.spec.path(
            path='/pet',
            operations={
                'get': {
                    'parameters': [{
                        'in': 'query',
                        'schema': PetSchema,
                    }],
                },
                'post': {
                    'parameters': [{
                        'in': 'body',
                        'schema': PetSchema,
                    }],
                },
            },
        )
        p = get_paths(spec_fixture.spec)['/pet']
        assert 'schema' not in p['get']['parameters'][0]
        post = p['post']
        assert len(post['parameters']) == 1
        assert post['parameters'][0]['schema']['$ref'] == self.ref_path(spec_fixture.spec) + 'Pet'

    @pytest.mark.parametrize('spec_fixture', ('3.0.0', ), indirect=True)
    def test_schema_uses_ref_in_parameters_and_request_body_if_available_v3(self, spec_fixture):
        spec_fixture.spec.components.schema('Pet', schema=PetSchema)
        spec_fixture.spec.path(
            path='/pet',
            operations={
                'get': {
                    'parameters': [{
                        'in': 'query',
                        'schema': PetSchema,
                    }],
                },
                'post': {
                    'requestBody': {
                        'content': {
                            'application/json': {
                                'schema': PetSchema,
                            },
                        },
                    },
                },
            },
        )
        p = get_paths(spec_fixture.spec)['/pet']
        assert 'schema' in p['get']['parameters'][0]
        post = p['post']
        schema_ref = post['requestBody']['content']['application/json']['schema']
        assert schema_ref == {'$ref': self.ref_path(spec_fixture.spec) + 'Pet'}

    @pytest.mark.parametrize('spec_fixture', ('2.0', ), indirect=True)
    def test_schema_array_uses_ref_if_available_v2(self, spec_fixture):
        spec_fixture.spec.components.schema('Pet', schema=PetSchema)
        spec_fixture.spec.path(
            path='/pet',
            operations={
                'get': {
                    'parameters': [{
                        'in': 'body',
                        'schema': {
                            'type': 'array',
                            'items': PetSchema,
                        },
                    }],
                    'responses': {
                        200: {
                            'schema': {
                                'type': 'array',
                                'items': PetSchema,
                            },
                        },
                    },
                },
            },
        )
        get = get_paths(spec_fixture.spec)['/pet']['get']
        len(get['parameters']) == 1
        resolved_schema = {
            'type': 'array',
            'items': {'$ref': self.ref_path(spec_fixture.spec) + 'Pet'},
        }
        assert get['parameters'][0]['schema'] == resolved_schema
        assert get['responses'][200]['schema'] == resolved_schema

    @pytest.mark.parametrize('spec_fixture', ('3.0.0', ), indirect=True)
    def test_schema_array_uses_ref_if_available_v3(self, spec_fixture):
        spec_fixture.spec.components.schema('Pet', schema=PetSchema)
        spec_fixture.spec.path(
            path='/pet',
            operations={
                'get': {
                    'parameters': [{
                        'in': 'body',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'array',
                                    'items': PetSchema,
                                },
                            },
                        },
                    }],
                    'responses': {
                        200: {
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'array',
                                        'items': PetSchema,
                                    },
                                },
                            },
                        },
                    },
                },
            },
        )
        p = get_paths(spec_fixture.spec)['/pet']
        assert 'get' in p
        op = p['get']
        resolved_schema = {
            'type': 'array',
            'items': {'$ref': self.ref_path(spec_fixture.spec) + 'Pet'},
        }
        request_schema = op['parameters'][0]['content']['application/json']['schema']
        assert request_schema == resolved_schema
        response_schema = op['responses'][200]['content']['application/json']['schema']
        assert response_schema == resolved_schema

    @pytest.mark.parametrize('spec_fixture', ('2.0', ), indirect=True)
    def test_schema_partially_v2(self, spec_fixture):
        spec_fixture.spec.components.schema('Pet', schema=PetSchema)
        spec_fixture.spec.path(
            path='/parents',
            operations={
                'get': {
                    'responses': {
                        200: {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'mother': PetSchema,
                                    'father': PetSchema,
                                },
                            },
                        },
                    },
                },
            },
        )
        get = get_paths(spec_fixture.spec)['/parents']['get']
        assert get['responses'][200]['schema'] == {
            'type': 'object',
            'properties': {
                'mother': {'$ref': self.ref_path(spec_fixture.spec) + 'Pet'},
                'father': {'$ref': self.ref_path(spec_fixture.spec) + 'Pet'},
            },
        }

    @pytest.mark.parametrize('spec_fixture', ('3.0.0', ), indirect=True)
    def test_schema_partially_v3(self, spec_fixture):
        spec_fixture.spec.components.schema('Pet', schema=PetSchema)
        spec_fixture.spec.path(
            path='/parents',
            operations={
                'get': {
                    'responses': {
                        200: {
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'mother': PetSchema,
                                            'father': PetSchema,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        )
        get = get_paths(spec_fixture.spec)['/parents']['get']
        assert get['responses'][200]['content']['application/json']['schema'] == {
            'type': 'object',
            'properties': {
                'mother': {'$ref': self.ref_path(spec_fixture.spec) + 'Pet'},
                'father': {'$ref': self.ref_path(spec_fixture.spec) + 'Pet'},
            },
        }


class TestCircularReference:

    def test_circular_referencing_schemas(self, spec):
        spec.components.schema('Analysis', schema=AnalysisSchema)
        spec.components.schema('Sample', schema=SampleSchema)
        spec.components.schema('Run', schema=RunSchema)
        definitions = get_definitions(spec)
        ref = definitions['Analysis']['properties']['sample']['$ref']
        assert ref == ref_path(spec) + 'SampleSchema'


class TestSelfReference:

    def test_self_referencing_field_single(self, spec):
        spec.components.schema('SelfReference', schema=SelfReferencingSchema)
        definitions = get_definitions(spec)
        ref = definitions['SelfReference']['properties']['single']['$ref']
        assert ref == ref_path(spec) + 'SelfReference'

    def test_self_referencing_field_many(self, spec):
        spec.components.schema('SelfReference', schema=SelfReferencingSchema)
        definitions = get_definitions(spec)
        result = definitions['SelfReference']['properties']['many']
        assert result == {
            'type': 'array',
            'items': {'$ref': ref_path(spec) + 'SelfReference'},
        }


class TestSchemaWithDefaultValues:
    def test_schema_with_default_values(self, spec):
        spec.components.schema('DefaultValuesSchema', schema=DefaultValuesSchema)
        definitions = get_definitions(spec)
        props = definitions['DefaultValuesSchema']['properties']
        # FIXME BS 2018-10-16: Test default values