#-------------------------------------------------------------------------------
# Name:        marketsim.py
# Purpose:     backtest based on orders, generate values
#              values = marketsim(starting_cash, orders)
#
# Author:      D. Gilbert
#
# Created:     16/04/2013
# Copyright:   (c) scubamut 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def marketsim(starting_cash, orders, data_path):

    import datetime as dt
    import pandas as pd
    import pandas.io.data as web
    from finlib.get_history import get_history

    symbols = list(set(orders.symbol))

    startday = min(orders.index)
    endday= max(orders.index)

    raw_data = get_history(symbols, startday, endday, data_path)

    prices = raw_data.ix[:,:,'Adj Close']

    # empty dfs for holdings and port_value
    holdings = pd.DataFrame(0, columns=symbols, index=prices.index)
    port_value = pd.DataFrame(0, columns=['Cash', 'Value', 'Total'], index=prices.index)

    for i in range(len(orders)):
        if orders.ix[i]['action'] == 'Buy':
            holdings.ix[orders.index[i]][orders.symbol[i]] += orders['qty'][i]
            port_value.ix[orders.index[i]]['Cash'] -= orders['qty'][i] * prices.ix[orders.index[i]][orders.symbol[i]]
        elif orders.ix[i]['action'] == 'Sell':
            holdings.ix[orders.index[i]][orders.symbol[i]] -= orders['qty'][i]
            port_value.ix[orders.index[i]]['Cash'] +=  orders['qty'][i] * prices.ix[orders.index[i]][orders.symbol[i]]
        else:
            print 'Bad order'
            raise

    port_value['Cash'][0] += starting_cash

    port_value = port_value.cumsum()
    holdings = holdings.cumsum()
    port_value['Value'] = (prices * holdings).sum(axis=1)
    port_value['Total'] = port_value.sum(axis=1)

    return port_value

if __name__ == '__main__':

    import pandas as pd
    import datetime as dt

    data_path = 'D:\\Google Drive\\Python Projects\\PyScripter Projects\\Computational Investing\Data\\'

    orders = pd.read_csv(data_path + 'orders.csv',header=None)
    orders.columns = ['year', 'month', 'day', 'symbol', 'action', 'qty', 'cash']

    dates = [dt.date(orders.year[i],orders.month[i],orders.day[i]) for i in range(len(orders))]

    # marketsim only needs symbol, Buy/Sell, qty
    orders = orders.ix[:,3:6]
    orders.index = dates

    values = marketsim(1000000, orders, data_path)


#    values.to_csv(data_path + 'values.csv')
