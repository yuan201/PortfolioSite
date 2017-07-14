import sys
import csv

def extract_symbols(file):
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        symbols = [tran['symbol']+","+tran['name'] for tran in reader]
        symbols = set(symbols)
        return symbols

def dump_symbols(symbols, file):
    with open(file, 'w') as f:
        symbols = [sym+'\n' for sym in symbols]
        f.writelines(symbols)

def usage():
    print("Usage:\n\t{} trans.csv, symbols.txt".format(sys.argv[0]))
            
if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
        exit()

    symbols = extract_symbols(sys.argv[1])
    dump_symbols(symbols, sys.argv[2])
    
