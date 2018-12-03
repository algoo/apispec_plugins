# coding: utf-8
import marshmallow

from tests.utils import get_definitions


class Person(marshmallow.Schema):
    first_name = marshmallow.fields.String()
    last_name = marshmallow.fields.String()
    phone_number = marshmallow.fields.String()


class Assembly(marshmallow.Schema):
    president = marshmallow.fields.Nested(Person)
    deputies = marshmallow.fields.Nested(Person, many=True, exclude=("phone_number",))


class TestSchemaClassResolving(object):
    def test_unit__reference_with_exclude__ok__nominal_case(self, spec):
        spec.components.schema("assembly", schema=Assembly)
        definitions = get_definitions(spec)

        pass
