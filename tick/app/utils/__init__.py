# coding: utf-8

from datetime import datetime, date
from itertools import tee


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def parse_date(date_in_text):
    """
    '10/30/2016' -> datetime.date(2016, 10, 30)
    :param date_in_text: str()
    :return: datetime.date()
    """
    try:
        return datetime.strptime(date_in_text, '%m/%d/%Y').date()
    except ValueError:
        return date.today()
