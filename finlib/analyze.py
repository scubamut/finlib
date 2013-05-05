#-------------------------------------------------------------------------------
# Name:        analyze.py
# Purpose:     to calculate Average Daily Return, Standard Deviation, Sharpe Ratio,
#               and Total Return of a set of portfolio values, together with
#               comparative Market Index (SPY) values for period
#
# Calling:     AR, SD, SR, TR = analyze(values, index_ticker='SPY')
#               values = portfolio values df - Cash, Equities, Total
#
#
# Author:      scubamut
#
# Created:     17/04/2013
# Copyright:   (c) scubamut 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def analyze(values, data_path, index_ticker='SPY', p_print='No'):

    import pandas as pd
    from finlib.get_history import get_history
    from math import sqrt

    idx_ticker = index_ticker
    values = values

    start = values.index.min()
    end = values.index.max()

    market_index = get_history([idx_ticker], start, end, data_path).ix[:,:,'Adj Close']
    market_index['d_rets'] = market_index[idx_ticker] / market_index[idx_ticker].shift(1) - 1

    values['d_rets'] = values['Total'] / values['Total'].shift(1) - 1

    metrics = [''] * 8

    metrics[0] = values['d_rets'].mean()
    metrics[4] = market_index['d_rets'].mean()

    metrics[1] =  values['d_rets'].std()
    metrics[5] = market_index['d_rets'].std()

    metrics[2] = sqrt(len(values['d_rets'])) * values['d_rets'].mean() / values['d_rets'].std()
    metrics[6] = sqrt(len(market_index['d_rets'])) * market_index['d_rets'].mean() / market_index['d_rets'].std()

    metrics[3] = values['Total'][-1] / values['Total'][0]
    metrics[7] = market_index['SPY'][-1] / market_index['SPY'][0]

    if p_print == 'Yes':

        print 'Date Range: ', start , 'to', end
        print
        print 'Final Value of Portfolio: ', values['Total'][-1]
        print
        print 'Sharpe Ratio: ', metrics[2]
        print 'Index Sharpe Ratio: ', metrics[6]
        print
        print 'Period Return: ', metrics[3]
        print 'Index Period Return: ', metrics[7]
        print
        print 'Volatilty: ', metrics[1]
        print 'Index Volatilty: ', metrics[5]
        print
        print 'Average Daily Return :', metrics[0]
        print 'Index Average Daily Return :', metrics[4]



    return metrics

if __name__ == '__main__':

    import pandas as pd
    from finlib.marketsim import marketsim

    data_path = 'G:\\Python Projects\\Computational Investing\\Data\\'

    orders = pd.read_csv(data_path + 'orders.csv',header=None)
    orders.columns = ['year', 'month', 'day', 'symbol', 'action', 'qty', 'cash']

    dates = [dt.date(orders.year[i],orders.month[i],orders.day[i]) for i in range(len(orders))]

    # marketsim only needs symbol, Buy/Sell, qty
    orders = orders.ix[:,3:6]
    orders.index = dates

    portfolio_values = marketsim(1000000, orders, data_path)

    metrics = analyze(portfolio_values, data_path, index_ticker='SPY', p_print='Yes')
