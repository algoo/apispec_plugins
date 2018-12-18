# coding: utf-8
import dataclasses
import typing


def schema_name_resolver(
    dataclass_: type,
    arguments: typing.Optional[tuple] = None,
    only: typing.Optional[typing.List[str]] = None,
    exclude: typing.Optional[typing.List[str]] = None,
) -> str:
    try:
        dataclass_name = dataclass_.__name__
    except AttributeError:
        dataclass_name = dataclass_.__origin__.__name__
        dataclass_ = dataclass_.__origin__
    only = only or []
    exclude = exclude or []
    excluded_field_names = exclude
    dataclass_field_names = [f.name for f in dataclasses.fields(dataclass_)]

    if only:
        for dataclass_field_name in dataclass_field_names:
            if dataclass_field_name not in only:
                excluded_field_names.append(dataclass_field_name)

    if not excluded_field_names:
        return dataclass_name

    return "{}_exclude_{}".format(dataclass_name, "_".join(excluded_field_names))
