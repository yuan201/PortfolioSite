import sys
import csv
from collections import namedtuple
import datetime as dt


Header = ['symbol','name','type_','date','shares','price',
          'cashvalue', 'fee', 'dividend', 'ratio','currency']
#Transaction = namedtuple('Transaction', Header)


def organize_zszq(file):
    lines = []
    with open(file, encoding='utf-8-sig') as csvfile:
        csvreader = csv.DictReader(csvfile, )
        for line in csvreader:
            #print(line)
            l = organize_line_zszq(line)
            if l['type_'] != 'invalid':
                lines.append(l)
    return lines


def organize_line_zszq(line):
    t = dict(
        symbol = line['证券代码'],
        name =  line['证券名称'],
        date = zszq_datetime(line['成交日期'], line['成交时间']),
        type_ = zszq_type(line['买卖标志']),
        shares = 0,
        price = 0,
        cashvalue = 0,
        fee = 0,
        dividend = 0,
        ratio = 0,
        currency='CNY',
    )

    if t['type_'] == 'buy':
        t['shares'] = int(line['成交数量'])
        t['price'] = float(line['成交价格'])
        t['cashvalue'] = -float(line['成交金额'])
    elif t['type_'] == 'sell':
        t['shares'] = int(line['成交数量'])
        t['price'] = float(line['成交价格'])
        t['cashvalue'] = float(line['成交金额'])
    elif t['type_'] == 'dividend':
        t['dividend'] = float(line['成交金额'])

    if len(t['symbol'])==5 and t['symbol'][0] == '0':
        t['symbol'] += '.HK'
    elif (t['symbol'].startswith('60') or t['symbol'].startswith('90') or
          t['symbol'].startswith('5')):
        t['symbol'] += '.SS'
    elif t['symbol'].startswith('00') or t['symbol'].startswith('20'):
        t['symbol'] += '.SZ'

    if t['symbol'].startswith('90'):
        t['currency'] = 'USD'
    if t['symbol'].startswith('20'):
        t['currency'] = 'HKD'
        
    return t


def zszq_type(type):
    if type == '股息入帐':
        return 'dividend'
    elif type == '买入':
        return 'buy'
    elif type == '卖出':
        return 'sell'
    else:
        return 'invalid'   

    
def zszq_datetime(date_, time_):
    year = int(date_[:4])
    month = int(date_[4:6])
    day = int(date_[6:])
    time_ = time_.split(':')
    hour = int(time_[0])
    minute = int(time_[1])
    second = int(time_[2])
    return dt.datetime(year, month, day, hour, minute, second)
    
    
def dumplines(lines, file):
    with open(file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=Header)
        writer.writeheader()
        for line in lines:
            writer.writerow(line)

def fillin_cashflow_zszq(cffile, lines):
    with open(cffile) as csvfile:
        cflines = []
        csvreader = csv.DictReader(csvfile)
        for line in csvreader:
            line['date'] = zszq_datetime(line['成交日期'], "00:00:00")
            cflines.append(line)

    cflines.sort(key=lambda x: x['date'])

    # find the matching cash flow record for each transaction line
    i = 0
    for line in lines:
        print(line)
        while line['date'] > cflines[i]['date']:
            i+=1
        while line['name'] != cflines[i]['证券名称']:
            i+=1
        # finding a matching record
        line['fee'] = cflines[i]['手续费'] + cflines[i]['印花税'] + \
	              cflines[i]['过户费'] + cflines[i]['结算费']
        line['cashflow'] = cflines[i]['发生金额']
        
            

def usage():
    print("Usage:\n  {} type infiles outfile".format(sys.argv[0]))
    exit()
            
if __name__ == "__main__":
    if len(sys.argv) < 4:
        usage()

    if sys.argv[1] == "zszq":
        lines = organize_zszq(sys.argv[2])
        lines.sort(key=lambda x: x['date'])
        if len(sys.argv) > 4:
            fillin_cashflow_zszq(sys.argv[3], lines)
        dumplines(lines, sys.argv[-1])
        
        
