from excel_loader.constants import FK_DEFAULT
from excel_loader.parsers import (
    get_boolean,
    get_integer,
    get_datetime,
    get_exact_string,
    get_float,
    get_percentage,
)


class ValueImporter:
    """
    Base class for field based on special parsing

    :cvar raw_value: Var with data without parsing
    :cvar mandatory_fields: Tuple that holds the names of required class init
        params
    :cvar field_to_set: Str with field name
    :cvar data_type: data type e.g. int or float
    :cvar parser_types: Dict with supported data types
    """

    raw_value = None
    mandatory_fields = tuple()
    field_to_set = None
    data_type = None
    parser_types = {
        bool: get_boolean,
        int: get_integer,
        float: get_float,
        str: get_exact_string,
        'datetime': get_datetime,
        '%': get_percentage,
        None: lambda x: x,
    }

    def __init__(self, **kwargs):
        """
        Initializer that sets the instance values

        :param kwargs: Dict with instance values to set
        """

        self.validate(**kwargs)
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def validate(self, **kwargs):
        """
        Function that validates the data sent is full from mandatory fields

        :cvar kwargs: dict with kwargs passed on the init function
        """

        if not self.mandatory_fields:
            raise AttributeError('Missing instance mandatory_fields var')
        for field in self.mandatory_fields:
            if field not in kwargs:
                raise AttributeError(f"Missing attribute {field}")

    def get_value(self, raw_value=None):
        """
        Function that returns the value already parsed by the correct parser

        :param raw_value: var to be parsed

        :return: var already on the correct format
        """

        return self.parser_types[self.data_type](raw_value)


class FieldImporter(ValueImporter):
    """
    ValueImporter for a simple field without much complexity

    :cvar mandatory_fields: tuple that sets the mandatory fields of the class
    """

    mandatory_fields = ('data_type',)


class ModelImporter(ValueImporter):
    """
    ValueImporter for fk fields
    - simple fields: e.g. ModelImporter(
        field_to_set='currency', lookup_field_name='code', model=Currency),
    - m2m fields: e.g. ModelImporter(
        field_to_set='accounts', lookup_field_name='ruc', model=Fund,
        fk_type='m2m', reverse=False)

    :cvar mandatory_fields: tuple that sets the mandatory fields of the class
    :cvar lookup_field_name: Str with key of value to search for
    :cvar model: Model instance to query
    :cvar fk_type: FK_M2M or FK from constants
    :cvar reverse: Bool, the relationship needs to be set on this model queried
    """

    mandatory_fields = ('field_to_set', 'lookup_field_name', 'model')
    lookup_field_name = None
    model = None
    fk_type = FK_DEFAULT
    reverse = False

    def get_value(self, raw_value=None):
        """
        Function that returns the model instance

        :param raw_value: Var of the value to search for

        :return: model instance
        """

        raw_value = raw_value if raw_value else self.raw_value
        if self.data_type:
            raw_value = super(ModelImporter, self).get_value(raw_value)

        if type(self.lookup_field_name) == list:
            parsed_values = raw_value.split(',')
            kwargs = {}
            for i in range(len(parsed_values)):
                lookup_field_item = self.lookup_field_name[i]
                if type(lookup_field_item) == FieldImporter:
                    kwargs[lookup_field_item.lookup_field_name] = lookup_field_item.get_value(
                        parsed_values[i])
                else:
                    kwargs[lookup_field_item] = parsed_values[i]

        else:
            kwargs = {self.lookup_field_name: raw_value}

        return self.model.objects.filter(**kwargs).first()


class NestedModelImporter(ValueImporter):
    """
    ValueImporter for a nested model on the same sheet

    :cvar mandatory_fields: tuple that sets the mandatory fields of the class
    """

    mandatory_fields = ('field_to_set', 'model')


