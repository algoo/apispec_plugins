# coding: utf-8
import dataclasses
import typing

import typing_inspect


def extract_name_of_dataclass(dataclass_: type) -> typing.Tuple[type, str]:
    try:
        dataclass_name = dataclass_.__name__
    except AttributeError:
        dataclass_name = dataclass_.__origin__.__name__

    return dataclass_name


def schema_name_resolver(
    dataclass_: type,
    arguments: typing.Optional[tuple] = None,
    only: typing.Optional[typing.List[str]] = None,
    exclude: typing.Optional[typing.List[str]] = None,
) -> str:
    if typing_inspect.is_generic_type(dataclass_):
        dataclass_name = extract_name_of_dataclass(dataclass_)
        dataclass_name += "_" + "_".join([
            arg.__name__ for arg in typing_inspect.get_args(dataclass_)
        ])
    else:
        dataclass_name = extract_name_of_dataclass(dataclass_)

    dataclass_origin = dataclass_
    try:
        dataclass_origin = dataclass_.__origin__
    except AttributeError:
        pass

    only = only or []
    exclude = exclude or []
    excluded_field_names = exclude
    dataclass_field_names = [f.name for f in dataclasses.fields(dataclass_origin)]

    if only:
        for dataclass_field_name in dataclass_field_names:
            if dataclass_field_name not in only:
                excluded_field_names.append(dataclass_field_name)

    if not excluded_field_names:
        return dataclass_name

    return "{}_exclude_{}".format(dataclass_name, "_".join(excluded_field_names))
