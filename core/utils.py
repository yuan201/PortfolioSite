import datetime as dt
import pandas as pd


def build_link(l, text):
    """
    A util function to create a href tag based on link and description text.
    """
    return "<a href={}>{}</a>".format(l, text)


# todo might move all datetime/date related utility functions to a separate package
def date_(datetime):
    return dt.datetime(datetime.year, datetime.month, datetime.day)


def last_business_day():
    return pd.Timestamp(dt.date.today(), offset='B')-1


def next_business_day(date):
    return pd.Timestamp(date, offset='B')+1


def to_business_timestamp(datetime):
    return pd.Timestamp(datetime, offset='B')