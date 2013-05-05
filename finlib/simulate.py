#-------------------------------------------------------------------------------
# Name:        simulate
# Purpose:
#
# Author:      scubamut
#
# Created:     14/04/2013
# Copyright:   (c) scubamut 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from math import sqrt
from finlib.get_history import get_history


def simulate(start, end, symbols, weights, data_path) :

    import pandas as pd

    # check data available, refresh if necessary
    get_history(symbols, start, end, data_path)

    pdata = pd.Panel(dict((symbols[i], pd.read_csv(data_path + symbols[i] + '.csv',\
                     index_col='Date', parse_dates=True).sort(ascending=True)) for i in range(len(symbols))) )

    starting_cash = 1000000

    # create empty dataframe with index = dates start-end
    df = pd.DataFrame(index=pdata.major_axis).ix[start:end]

    for i in range(len(symbols)):
        ticker = symbols.ix[i]
        allocation = weights[i]
        df[ticker] = pdata[ticker]['Adj Close']
        df[ticker + ' C'] = df[ticker] / df[ticker][0]
        df[ticker + ' C'][0] = 1.
        df[ticker + ' I'] = 0.
        df[ticker + ' I'][0] = starting_cash * allocation
        df[ticker + ' I'] = [df[ticker + ' C'][j] * df[ticker + ' I'][0] for j in range(len(df))]

    df['Total'] =pd.DataFrame([df[ticker + ' I'] for ticker in symbols]).sum()
    df['Daily Rets'] = df.Total / df.Total.shift(1) - 1

    Average_Daily_Return = df['Daily Rets'].mean()
    Volatilty = df['Daily Rets'].std()
    Sharpe_Ratio = sqrt(len(df)) * df['Daily Rets'].mean() / df['Daily Rets'].std()
    Period_Return = df.Total[-1] / df.Total[0] - 1

    return Average_Daily_Return, Volatilty, Sharpe_Ratio, Period_Return

def main():
    pass

if __name__ == '__main__':

    import pandas as pd
    import datetime as dt
    from finlib.simulate import simulate

    data_path = 'G:\\Python Projects\\Computational Investing\\Data\\'
    tickers = pd.read_csv(data_path + 'tickers.csv')

    start_date = '1/1/2011'
    end_date = '31/12/2011'

    start = dt.datetime.strptime(start_date, '%d/%m/%Y').date()
    end = dt.datetime.strptime(end_date, '%d/%m/%Y').date()

    symbols = tickers.ticker
    weights = tickers.allocations

    Average_Daily_Return, Volatilty, Sharpe_Ratio, Period_Return = simulate(start, end, symbols, weights, data_path)

    print 'Symbols: ', symbols
    print 'Weights: ', weights
    print 'Start Date: ', start_date
    print 'End Date: ', end_date
    print 'Data Directory: ', data_path
    print 'Average Daily Return :', Average_Daily_Return
    print 'Volatilty: ', Volatilty
    print 'Sharpe Ratio: ', Sharpe_Ratio
    print 'Period Return: ', Period_Return
