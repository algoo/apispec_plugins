# coding: utf-8
import dataclasses

import typing

from apispec_serpyco.utils import schema_name_resolver


def test_schema_name_resolver__nominal_case():
    @dataclasses.dataclass
    class Foo:
        pass

    assert "Foo" == schema_name_resolver(Foo)


def test_schema_name_resolver__exclude():
    @dataclasses.dataclass
    class Foo:
        bar: str

    assert "Foo_exclude_bar" == schema_name_resolver(Foo, exclude=["bar"])


def test_schema_name_resolver__include():
    @dataclasses.dataclass
    class Foo:
        bar: str
        baz: str

    assert "Foo_exclude_bar" == schema_name_resolver(Foo, only=["baz"])


def test_schema_name_resolver__generic_type():
    @dataclasses.dataclass
    class Foo:
        bar: str

    T = typing.TypeVar("T")

    @dataclasses.dataclass
    class Bar(typing.Generic[T]):
        items: typing.List[T]

    assert "Bar_Foo" == schema_name_resolver(Bar[Foo])


def test_schema_name_resolver__args_generic_type():
    @dataclasses.dataclass
    class Foo:
        bar: str

    T = typing.TypeVar("T")

    @dataclasses.dataclass
    class Bar(typing.Generic[T]):
        items: typing.List[T]

    assert "Bar_Foo_int" == schema_name_resolver(Bar[Foo], [int])
