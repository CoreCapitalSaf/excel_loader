from django.db import IntegrityError

from excel_loader.constants import FK_M2M
from excel_loader.exceptions import ImporterError, ImporterIntegrityException
from excel_loader.types import (
    FieldImporter,
    ModelImporter,
    NestedModelImporter,
    FileImporter,
)


class ExcelSheetParser(object):
    """
    Base class for the parser object that every model_parsers on the app should
    inherit from to be a model class parser from excels

    e.g. {'pre': pre, 'post': post}

    :cvar model: models.Model instance e.g. User
    :cvar fields: dict that contains the mapping from the excel sheet to the
        field e.g. fields = {0:'number', 1:'fund_type'} where 0 should match the
        alphabetical column 0=A.
    :cvar extra_operations: dict with functions
    :cvar field_to_set: str used for foreign key post operations if needed
    """

    model = None
    fields = {}
    extra_operations = {}
    field_to_set = None

    def __init__(self):
        self.extra_operations = {
            key: value.__get__(object) for key, value in
            self.extra_operations.items()}

    def pre(self, fields, inverse_relations=None):
        """
        Function in charge of the pre save operations, here extra field
        variables can be added for the importing instance e.g.

        def pre(self, fields, inverse_relations=[]):
            fields['state'] = User.ACTIVE
            fields['fk_field'] = inverse_relations[0].get_value().fk_field
            return fields

        :cvar fields: dict containing the kwargs to be saved, add extra fields
            variables e.g static variables set due to importing exceptions
        :cvar inverse_relations: list with ModelImporters inverse relations, on
            the ModelImporter instance can be loaded with a fk model fk field
            e.g. an instance fk instance we need it to be the same due to
            importing
        """

        return fields

    def post(self, instance, nested_fields):
        """
        Function in charge of the post save operations e.g.

        def post(self, instance, nested_fields):
            field = nested_fields[0].field_to_set
            value = nested_fields[0].get_value()
            User.objects.create(self.field_to_set=instance, field=value)

        :param instance: model instance to be added on nested object trying to
            save
        :param nested_fields: list stacked with NestedModelImporter to be added
            after the main model has already been created
        """

        pass


class DataParser:
    """
    Class that parses xlsx sheet,
    #todo: add autodiscover on the apps where model_parsers classes are

    :cvar base_types: tuple with classes to be processed on the set_field
        function, if custom ValueImporters are added, add them on this class
        custom implementation
    """

    base_types = (
        FieldImporter, ModelImporter, NestedModelImporter, FileImporter)

    def __init__(self, sheet_parser, sheet):
        """
        Initializer with core data to parse

        :param sheet_parser: ExcelSheetParser implemented classes on
            model_parsers.py apps
        :param sheet: xlrd.sheet.Sheet with raw data
        """

        self.sheet = sheet
        self.sheet_parser = sheet_parser

    @staticmethod
    def set_field(parser, instance_kwargs, value, m2m_objects=None,
                  inverse_relations=None, nested_fields=None):
        """
        Function that sets all the variables on the instance kwargs and dynamic
        variables to then return them to reference them

        :cvar parser: ExcelSheetParser implementation instance for the field
        :cvar instance_kwargs: dict containing the filling kwargs for the
            instance
        :cvar value: var extracted from the xlsx cell e.g A1
        :cvar m2m_objects: list containing the fields to be filled as m2m field
        :cvar inverse_relations: list containing the relations to be added from
            the Model class where it was defined OtherModel --> ThisModel
        :cvar nested_fields: list that contains NestedModelImporter fields to be
            added on the post function
        """

        if type(parser) == NestedModelImporter:
            parser.raw_value = value
            nested_fields.append(parser)
        elif type(parser) == FieldImporter:
            instance_kwargs[parser.field_to_set] = parser.get_value(value)
        elif type(parser) == FileImporter:
            instance_kwargs[parser.field_to_set] = parser.get_value(value)
        elif type(parser) == ModelImporter:
            if not parser.reverse:
                if parser.fk_type == 'm2m':
                    parser.raw_value = value
                    m2m_objects.append(parser)
                else:
                    instance_kwargs[parser.field_to_set] = parser.get_value(
                        value)
            else:
                parser.raw_value = value
                inverse_relations.append(parser)

        return (
            parser, instance_kwargs, value, m2m_objects, inverse_relations,
            nested_fields
        )

    def parse(self):
        """
        Function that parses itself all the data from the sheet and the
        ExcelSheetParser classes implementations on the model_parsers.py file
        and saves it for each model

        :raise: ImporterError if fails
        """

        sheet_parser = self.sheet_parser()
        for row_index in range(1, self.sheet.nrows):
            instance_kwargs = dict()
            inverse_relations = list()
            m2m_objects = list()
            nested_fields = list()

            for col_index in range(self.sheet.ncols):
                if not row_index:
                    continue
                value = self.sheet.cell(row_index, col_index).value
                parser = self.sheet_parser.fields[col_index]
                if type(parser) in self.base_types:
                    (parser, instance_kwargs, value, m2m_objects,
                     inverse_relations, nested_fields) = self.set_field(
                        parser, instance_kwargs, value, m2m_objects,
                        inverse_relations, nested_fields)
                else:
                    instance_kwargs[parser] = value
            if instance_kwargs: # save model block
                try:
                    has_eo = hasattr(sheet_parser, 'extra_operations')
                    if has_eo and 'pre' in sheet_parser.extra_operations:
                        instance_kwargs = sheet_parser.extra_operations['pre'](
                            fields=instance_kwargs,
                            inverse_relations=inverse_relations)
                    instance = self.sheet_parser.model(**instance_kwargs)
                    instance.save()
                except IntegrityError:
                    raise ImporterIntegrityException(
                        self.sheet_parser.model.__name__, instance_kwargs)

                if has_eo and 'post' in sheet_parser.extra_operations:
                    sheet_parser.extra_operations['post'](
                        instance, nested_fields)

                for obj in m2m_objects:
                    field = getattr(instance, obj.field_to_set)
                    field.add(obj.get_value())

                for inverse_importer in inverse_relations:
                    if inverse_importer.fk_type == FK_M2M:
                        try:
                            reverse_instance = inverse_importer.get_value()
                            field = getattr(
                                reverse_instance, inverse_importer.field_to_set)
                            field.add(instance)
                        except AttributeError:
                            raise AttributeError(inverse_importer.raw_value)


class ExcelCommandLoader:
    """
    Class to be called on the command implementation class of the handle
    function e.g.

    sheets_funds = {'Sheet name': SheetNameExcelSheetParser}
    wb = xlrd.open_workbook(options['file_path'])
    ExcelCommandLoader(sheets_funds, wb).load()

    :cvar sheet: dict with names as dict and ExcelSheetParser implementations
        e.g. {'Sheet name': CustomExcelSheetParser}
    :cvar wb: workbook object e.g. xlrd.open_workbook('file.xlsx')
    """

    sheets_funds = {}
    wb = None

    def __init__(self, sheets, wb):
        """Function defined to be overloaded on a future if needed"""
        self.sheets = sheets
        self.wb = wb

    def load(self):
        """
        Function that iterates every object on the sheets variable and begins to
        load the data on the database
        """

        try:
            for sheet_name in self.sheets:
                sheet = self.wb.sheet_by_name(sheet_name)
                sheet_parser = self.sheets[sheet_name]
                DataParser(sheet_parser, sheet).parse()
        except ImporterError as e:
            raise ImporterError(
                e.sheet_name, e.row_index, e.instance_kwargs, e.message)

