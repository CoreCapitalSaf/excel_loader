from django.db import IntegrityError


class ImporterError(Exception):
    """
    Importer exception with data to display needed
    #todo: add more specified errors
    """

    def __init__(self, sheet_name, row_index, instance_kwargs={}, message=''):
        """
        Initializer function with core data for the displayer on the commands

        :param sheet_name: Str with name
        :param row_index: Int with row number
        :param instance_kwargs: Dict with kwargs of the model to be saved
        :param message: Str with error message
        """

        self.sheet_name = sheet_name
        self.row_index = row_index
        self.instance_kwargs = instance_kwargs
        self.message = message


class ImporterIntegrityException(IntegrityError):
    """
    IntegrityError for the model creation block
    """

    def __init__(self, model_name, row_data):
        """todo: add error message class to display all as a warning"""
        self.model_name = model_name
        self.row_data = row_data