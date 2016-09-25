import datetime as dt


def build_link(l, text):
    """
    A util function to create a href tag based on link and description text.
    :param l:
    :param text:
    :return link:
    """
    return "<a href={}>{}</a>".format(l, text)


def _date(datetime):
    return dt.datetime(datetime.year, datetime.month, datetime.day)
