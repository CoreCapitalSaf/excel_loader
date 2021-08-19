from django.utils.dateparse import parse_datetime


def get_boolean(value):
    """
    Function the gets a boolean value from a string

    :param value: str with the boolean value

    :return: bool with the boolean value
    """

    bool_value = {
        'SI': True,
        'NO': False,
        'YES': True,
        'Y': True,
        'N': False,

    }

    return bool_value.get(value.upper(), False)


def get_integer(value):
    """
    Functions that gets an integer value from a string or decimal

    :param value: str or decimal value from the cell

    :return: int with integer value
    """

    try:
        value = int(value)
    except:
        value = 0

    return value


def get_float(value):
    """
    Function that gets a float value from a string (or decimal)

    :param value: str (or decimal) value from the cell

    :return: float value
    """

    try:
        value = float(value)
    except:
        value = 0

    return value


def get_datetime(value, convert_from_date=True):
    """
    Function that gets the datetime from any date this forms
    - '2008-04-19 11:47:58-05'
    - '2008-04-19'
    - '19/04/2008'

    :param value: str with date to parse
    :param convert_from_date: bool if is a date

    :return: Datetime value
    """

    try:
        if '/' in value:
            dd, mm, aa = value.split('/')
            value = parse_datetime(f"{aa}-{mm}-{dd} 00:00:00-00")
        elif convert_from_date:
            value = parse_datetime(f"{value} 00:00:00-00")
        else:
            value = parse_datetime(value)
    except Exception:
        value = None

    return value


def get_exact_string(value, max_len=50):
    """
    Function that gets string, without decimals points in case
    the value is decimal. It is used when an id is in a cell.

    :param value: str or decimal value
    :param max_len: int with the max length of the value

    :return: str with the correct string value
    """

    if not value:
        return ''
    value = str(value).split('.')[0] #todo: this .decimal removal should be done on get_float

    return value[:max_len]


def get_percentage(value):
    """
    Functions that gets an percentage from a numeric value out of a string or
    decimal

    :param value: str or decimal value from the cell

    :return: int with integer value
    """

    try:
        if value <= 1:
            value *= 100
        value = int(value)
    except:
        value = 0

    return value

