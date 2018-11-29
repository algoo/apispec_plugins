# coding: utf-8
import dataclasses


def schema_name_resolver(dataclass_, only=None, exclude=None) -> str:
    # TODO BS 2018-11-27: Prevent Serpyco bug (who can call here with scalar types)
    if not dataclasses.is_dataclass(dataclass_):
        return dataclass_.__name__

    dataclass_name = dataclass_.__name__
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
