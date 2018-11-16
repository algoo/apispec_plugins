# coding: utf-8


def get_definitions(spec):
    if spec.openapi_version.major < 3:
        return spec.to_dict()['definitions']
    return spec.to_dict()['components']['schemas']


def get_parameters(spec):
    if spec.openapi_version.major < 3:
        return spec.to_dict()['parameters']
    return spec.to_dict()['components']['parameters']


def get_responses(spec):
    if spec.openapi_version.major < 3:
        return spec.to_dict()['responses']
    return spec.to_dict()['components']['responses']


def get_paths(spec):
    return spec.to_dict()['paths']


def ref_path(spec):
    if spec.openapi_version.version[0] < 3:
        return '#/definitions/'
    return '#/components/schemas/'
