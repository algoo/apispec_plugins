# coding: utf-8


def get_definitions(spec):
    if spec.openapi_version.major < 3:
        return spec.to_dict().get("definitions", {})
    return spec.to_dict().get("components", {}).get("schemas", {})


def get_parameters(spec):
    if spec.openapi_version.major < 3:
        return spec.to_dict().get("parameters", {})
    return spec.to_dict().get("components", {}).get("parameters", {})


def get_responses(spec):
    if spec.openapi_version.major < 3:
        return spec.to_dict().get("responses", {})
    return spec.to_dict().get("components", {}).get("responses", {})


def get_paths(spec):
    return spec.to_dict()["paths"]


def ref_path(spec):
    if spec.openapi_version.version[0] < 3:
        return "#/definitions/"
    return "#/components/schemas/"
