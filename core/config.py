import datetime as dt

# todo move config to database (maybe after adding multi-user support)
INIT_DATE = dt.date(2015, 1, 1)

CURRENCY_CHOICES = (
    ('CNY', 'Chinese Yuan'),
    ('USD', 'US Dollar'),
    ('HKD', 'HK Dollar'),
)

BASE_CURRENCY = 'CNY'

STOCK_EXCHANGES = (
    ('SSE', 'Shanghai Stock Exchange'),
    ('SZSE', 'Shenzhen Stock Exchange'),
    ('NYSE', 'Newyork Stock Exchange'),
    ('NASDAQ', 'Nasdaq Stock Market'),
    ('HKEX', 'Hongkong Stock Exchange')
)

EXCHANGE_DEFAULT_QUOTER = {
    "SSE": "Tushare",
    "SZSE": "Tushare",
    "NYSE": "pandas",
    "NASDAQ": "pandas",
    "HKEX": "pandas",
}

DAYS_IN_A_YEAR = 261
# 261 business days in a year, confirmed with Pandas