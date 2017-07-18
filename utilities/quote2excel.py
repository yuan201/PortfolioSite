###############################################
# use tushare to get quotes
# and save to csv for excel
# only workon for stocks listed
# in Shanghai and Shenzheng Exchange
###############################################

import tushare as ts
import pandas as pd
import csv
from collections import namedtuple
import datetime as dt
import sys
from pathlib import Path

Security = namedtuple('Security',
                      ['symbol','exchange','name','index','longname'])

# load symbols from csv file
def read_symbol_file(file):
    securities = {}
    with open(file) as csvfile:
        sym_reader = csv.reader(csvfile)
        for row in sym_reader:
            if len(row) == 2:
                se = row[0].split('.')
                securities[row[0]] = Security(se[0],se[1],row[1],
                                              len(se)==3,row[0])
    return securities


# get quotes from tushare and put into a DataFrame
def get_quotes(securities, daterange):
    quotes = pd.DataFrame(index=daterange)
    for sec in securities.values():
        # for those listed on Shanghai or Shengzheng,
        # Tushare is used to get the data
        if sec.exchange == 'SS' or sec.exchange == 'SZ':
            quote = ts.get_k_data(code=sec.symbol,
                                  autype=None, index=sec.index);
            quote = convert_date(quote)
            quotes[sec.longname] = quote['close']
        # or those listed in HK, data is only available through
        # yahoo right now and the pandas datareader is broken
        # so I have to download them manually and import them here.
        elif sec.exchange == 'HK':
            p = Path('hkquotes/{}.HK.csv'.format(sec.symbol[1:]))
            if not p.exists():
                print("{} doesn't exist".format(p))
            else:
                quotes[sec.longname] = parse_hk_quote(sec, p)['close']
    return quotes

def parse_hk_quote(sec, quotefile):
    quote = pd.read_csv(quotefile)
    newcolumns = [col.lower() for col in quote.columns]
    quote.columns = newcolumns
    return convert_date(quote)

# date from tushare is just orinary string, need to convert
def convert_date(quote):
    quote['date'] = pd.to_datetime(quote['date'])
    quote.set_index('date', inplace=True)
    return quote
    

# save quotes to csv file
def save_quotes(quotes,file):
    pass


def usage():
    print("usage:\n{} symbols.csv startdate enddate quotes.csv".format(
        sys.argv[0]))

def addname(csvlist, secs):
    names = [secs[i].name for i in csvlist[0].split(',')[1:]]
    namestr = ',' + ','.join(names)
    csvlist.insert(1, namestr)
    return csvlist

def save2csv(csvlist, csvfile):
    with open(csvfile, 'w', encoding='utf-8') as file:
        file.write('\n'.join(csvlist))

if __name__ == '__main__':
    if len(sys.argv) != 5:
        usage()
        exit()
    secs = read_symbol_file(sys.argv[1])
    daterange = pd.date_range(sys.argv[2], sys.argv[3])
    quotes = get_quotes(secs, daterange)
    quotes.fillna(method='ffill', inplace=True)
    csvlist = quotes.to_csv().split()
    csvlist = addname(csvlist, secs)
    save2csv(csvlist, sys.argv[4])
