# coding: utf-8
import marshmallow


def get_excluded_params(schema):
    """
    Get all params excluded in this schema,
    if "only" is provided in schema instance,
    consider all not included params as excluded.
    :param schema: instance or cls schema
    :return: set of excluded params
    """
    if isinstance(schema, type):
        return set()

    exclude = set()
    only = set()
    if getattr(schema, 'exclude', ()):
        exclude = set(getattr(schema, 'exclude', ()))
    if getattr(schema, 'only', ()):
        only = set(getattr(schema, 'only', ()))
    if only:
        for field in schema._declared_fields:
            if field not in only:
                exclude.add(str(field))
    return exclude


def generate_id(schema, exclude=()):
    """
    Generate id in order to distinct 2 schemas, instance
    or cls.
    :param schema: base_schema
    :param exclude: excluded fields
    :return: str id related to schema and exclude params
    """
    schema_id = ''
    if isinstance(schema, type):
        schema_id += schema.__name__
    else:
        schema_id += type(schema).__name__

    # fields
    fields = [field for field in schema._declared_fields.keys()
              if field not in exclude]
    fields = sorted(fields)
    schema_id += '('
    for field in fields:
        schema_id += '_' + str(field)
    schema_id += ')'

    return schema_id


def schema_class_resolver(
    marshmallow_plugin,
    schema,
):
    """
    Return best candidate class for a schema instance or cls.
    :param spec: Apispec instance
    :param schema: schema instance or cls
    :return: best schema cls
    """
    if isinstance(schema, type):
        return schema

    # Get instance params
    exclude = get_excluded_params(schema)

    cls_schema = type(schema)

    # generate id
    schema_id = generate_id(schema, exclude)

    # same as class schema ?
    if generate_id(cls_schema) == schema_id:
        return cls_schema

    # FIXME BS 2018-11-22: Must be in real code
    if not hasattr(marshmallow_plugin, 'auto_generated_schemas'):
        marshmallow_plugin.auto_generated_schemas = {}

    # already generated similar schema ?
    if schema_id in marshmallow_plugin.auto_generated_schemas:
        return marshmallow_plugin.auto_generated_schemas[schema_id]

    # no similar schema found, create new one
    class NewSchema(cls_schema):
        pass

    NewSchema.opts.exclude = exclude
    NewSchema.__name__ = cls_schema.__name__
    NewSchema._schema_name = '{}_{}'.format(
        cls_schema.__name__,
        id(NewSchema),
    )
    marshmallow_plugin.auto_generated_schemas[schema_id] = NewSchema
    return NewSchema


def generate_schema_name(schema: marshmallow.Schema):
    """
    Return best candidate name for one schema cls or instance.
    :param schema: instance or cls schema
    :return: best schema name
    """
    if not isinstance(schema, type):
        schema = type(schema)

    if getattr(schema, '_schema_name', None):
        if schema.opts.exclude:
            schema_name = "{}_without".format(schema.__name__)
            for elem in sorted(schema.opts.exclude):
                schema_name = "{}_{}".format(schema_name, elem)
        else:
            schema_name = schema._schema_name
    else:
        schema_name = schema.__name__

    return schema_name
