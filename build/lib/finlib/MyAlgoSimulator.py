import os, sys, datetime as dt
from pandas.lib import to_datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas.io.data as web
from pylab import *
from finlib import *

###############################################################################
# useful utility routine
def side_by_side(*objs, **kwds):
    from pandas.core.common import adjoin
    space = kwds.get('space', 4)
    reprs = [repr(obj).split('\n') for obj in objs]
    print adjoin(space, *reprs)

plt.rc('figure', figsize=(10, 7))
###############################################################################
# routine to output results from MarkowitzPortfolio Optimizer
def show_results(myPortfolio) :
    print '\n ##### meanReturns\n\n', myPortfolio.meanReturns
    print '\n ##### varianceCovarianceReturns\n\n', myPortfolio.varianceCovarianceReturns
    print '\n ##### estimate\n\n', myPortfolio.estimate
    print '\n ##### minVarianceWeights\n\n', myPortfolio.minVarianceWeights
    print '\n ##### globalMinimumVariance\n\n', myPortfolio.globalMinimumVariance
    print '\n ##### ComputeMinVariance\n\n', myPortfolio.ComputeMinVariance(0.02)
    print '\n ##### 5% VaR\n\n', myPortfolio.VaR(.05)
    print '\n ##### Efficient Frontier Plot\n\n'
    myPortfolio.plot()
##############################################################################
def optimize(strat_data, rebalance_dates, portfolio_symbols, lookback=60, leverage=1):

    # This section uses Markowitz optimization to determine weights

    portfolio_weights = pd.DataFrame(0.0, index=portfolio_symbols.index,\
                                      columns=portfolio_symbols.columns)
    for date in rebalance_dates :
    #    print date
    #    print portfolio_symbols.ix[date]
    #    print portfolio_symbols.ix[date].sum()
        no_of_symbols = portfolio_symbols.ix[date].sum()
        opt_symbols = [sym for sym in portfolio_symbols if\
                        portfolio_symbols.ix[date][sym] == 1]
        if no_of_symbols > 1 :
            weights = [float(leverage) / no_of_symbols] * no_of_symbols
    #        print 'opt_symbols = ',opt_symbols
            # start and end dates for optimization
            opt_start_date = strat_data['Close']\
                            .index[strat_data['Close']\
                            .index.searchsorted(date) - lookback]\
                            .strftime('%d/%m/%Y')
            opt_end_date = date.strftime('%d/%m/%Y')
    #        print opt_start_date, opt_end_date
            # determine optimal weights
            portfolio = MarkowitzPortfolio(opt_start_date, opt_end_date, "daily", opt_symbols, weights, 100000, data_path)
            # these are the global min variance weights
    #        print portfolio.globalMinimumVariance.ix[0][0:no_of_symbols]
            for symbol in portfolio.globalMinimumVariance.ix[0][0:no_of_symbols].keys() :
    #            print date, 'symbol = ', symbol, 'weight = ', portfolio.globalMinimumVariance.ix[0][symbol]
                portfolio_weights.ix[date][symbol] = float(portfolio.globalMinimumVariance.ix[0][symbol])
    #            print 'portfolio_weights.ix[', date, '][', symbol, '] = portfolio.globalMinimumVariance.ix[0][', symbol, ']'
        else :
    #        print date, 'symbol = ', opt_symbols[0], 'weight = 1.0'
            portfolio_weights.ix[date][opt_symbols[0]] = float(1.0)

    return portfolio_weights
############################################################################
def backtest(starting_cash, orders, sell_prices, buy_prices, portfolio_symbols, portfolio_weights, data_path):

    # empty dfs for portfolio_holdings and port_value
    portfolio_holdings = pd.DataFrame(columns=portfolio_symbols.columns, index=portfolio_symbols.index)
    port_value = pd.DataFrame(columns=['Cash', 'Value', 'Total'], index=portfolio_symbols.index)
    port_value['Cash'][0] = starting_cash

    for i in range(len(orders)):

        date = orders.index[i]
    ##############################################################################
    # breakpoint for debugging
#        if date == dt.datetime(2007,1,4):
#            pass
    ##############################################################################
        symbol = orders.ix[i]['symbol']
        qty = orders.ix[i]['qty']

        if orders.ix[i]['action'] == 'Rebalance1' : # this is for strict rebalance by weights

            # all current holdings are "liquidated" and "liquidated value" used to buy "new" shares by weight
            for symbol in [sym for sym in symbols if isnan(portfolio_holdings.ix[date][sym]) == False] :
                qty = portfolio_holdings.ix[date][symbol]
                # treat nan as 0
                if isnan(portfolio_holdings.ix[date][symbol]) :
                    portfolio_holdings.ix[date][symbol] = 0
                portfolio_holdings.ix[date][symbol] -= qty
                # assume selling at BUY price for rebalance (eg in the case of
                # a single share, nothing would be sold or bought

                port_value.ix[date]['Cash'] += qty * buy_prices.ix[date][symbol]
                print date, orders.ix[i]['action'], symbol,\
                 'SELL', qty, '@ ', buy_prices.ix[date][symbol], \
                 'REMAINING', portfolio_holdings.ix[date][symbol]\
                  , 'Cash = ', port_value.ix[date]['Cash']
            liquidation_value = port_value.ix[date]['Cash']
            # then buy using new symbols and weights
            for symbol in [sym for sym in symbols if portfolio_symbols.ix[date][sym] == 1] :
#                qty = int(port_value.ix[date]['Cash']\
                qty = liquidation_value * portfolio_weights.ix[date][symbol]\
                        / buy_prices.ix[date][symbol]
                if isnan(portfolio_holdings.ix[date][symbol]) :
                    portfolio_holdings.ix[date][symbol] = 0
                portfolio_holdings.ix[date][symbol] += qty
                port_value.ix[date]['Cash'] -= qty * buy_prices.ix[date][symbol]
                print date, orders.ix[i]['action'], symbol,\
                 'BUY', qty, '@ ', buy_prices.ix[date][symbol], \
                 'REMAINING', portfolio_holdings.ix[date][symbol]\
                  , 'Cash = ', port_value.ix[date]['Cash']

        elif orders.ix[i]['action'] == 'Rebalance2' : # hold shares if in last rebalance portfolio
                                                    # rebalance the remainder in equal proportions

            # shares in portfolio for this rebalance date
            this = [sym for sym in symbols if portfolio_symbols.ix[date][sym] > 0]
            # shares in portfolio at last rebalance date
            if date == rebalance_dates[0] :
                last = []
            else :
                last = [sym for sym in symbols if portfolio_symbols.ix[portfolio_holdings.index.searchsorted(date) - 1][sym] > 0]

            # only shares in 'last' and not in 'this' are "liquidated"
            # and "liquidated value" used to buy shares in 'this' not in last in equal proportions
            for symbol in [sym for sym in last if sym not in this] :
                qty = portfolio_holdings.ix[date][symbol]
                # treat nan as 0
                if isnan(portfolio_holdings.ix[date][symbol]) :
                    portfolio_holdings.ix[date][symbol] = 0
                portfolio_holdings.ix[date][symbol] -= qty
                port_value.ix[date]['Cash'] += qty * sell_prices.ix[date][symbol]
                print date, orders.ix[i]['action'], symbol,\
                 'SELL', qty, '@ ', buy_prices.ix[date][symbol], \
                 'REMAINING', portfolio_holdings.ix[date][symbol]\
                  , 'Cash = ', port_value.ix[date]['Cash']
            pass

            if len([sym for sym in this if sym not in last]) > 0 :
                # divide available cash equally
                weight_per_share = 1. / len([sym for sym in this if sym not in last])

                # this is the available cash
                liquidation_value = port_value.ix[date]['Cash']

                # now buy new shares
                for symbol in [sym for sym in this if sym not in last] :
                    qty = liquidation_value * weight_per_share\
                        / buy_prices.ix[date][symbol]
                    if isnan(portfolio_holdings.ix[date][symbol]) :
                            portfolio_holdings.ix[date][symbol] = 0
                    portfolio_holdings.ix[date][symbol] += qty
                    port_value.ix[date]['Cash'] -= qty * buy_prices.ix[date][symbol]
                    print date, orders.ix[i]['action'], symbol,\
                        'BUY', qty, '@ ', buy_prices.ix[date][symbol], \
                        'REMAINING', portfolio_holdings.ix[date][symbol]\
                        , 'Cash = ', port_value.ix[date]['Cash']
                else :
                    pass


        elif orders.ix[i]['action'] == 'Buy':
            # 'Buy' with no symbol specified implies buying portfolio_symbols set to 1 with appropiriate weights
            if is_string_like(symbol) == False :
                # use available cash
                available_cash = port_value.ix[date]['Cash']
                for symbol in [sym for sym in symbols if portfolio_symbols.ix[date][sym] == 1] :
                    qty = int(available_cash\
                               * portfolio_weights.ix[date][symbol]\
                                / buy_prices.ix[date][symbol])
                    if isnan(portfolio_holdings.ix[date][symbol]) :
                        portfolio_holdings.ix[date][symbol] = 0
                    portfolio_holdings.ix[date][symbol] += qty
                    port_value.ix[date]['Cash'] -= qty * buy_prices.ix[date][symbol]
                    print date, orders.ix[i]['action'], symbol,\
                     'BUY', qty, '@ ', buy_prices.ix[date][symbol], \
                     'REMAINING', portfolio_holdings.ix[date][symbol]\
                      , 'Cash = ', port_value.ix[date]['Cash']

            else :
                if isnan(portfolio_holdings.ix[date][symbol]) :
                    portfolio_holdings.ix[date][symbol] = 0
                portfolio_holdings.ix[date][symbol] += qty
                port_value.ix[date]['Cash'] -= qty * buy_prices.ix[date][symbol]
                print date, orders.ix[i]['action'], symbol,\
                 'BUY', qty, '@ ', buy_prices.ix[date][symbol], \
                 'REMAINING', portfolio_holdings.ix[date][symbol]\
                  , 'Cash = ', port_value.ix[date]['Cash']

        elif orders.ix[i]['action'] == 'Sell':
            if is_string_like(symbol) == False :
                # liquidate
                for symbol in [sym for sym in symbols if isnan(portfolio_holdings.ix[date][sym]) == False] :
                    qty = portfolio_holdings.ix[date][symbol]
                    if isnan(portfolio_holdings.ix[date][symbol]) :
                        portfolio_holdings.ix[date][symbol] = 0
                    portfolio_holdings.ix[date][symbol] -= qty
                    port_value.ix[date]['Cash'] += qty * sell_prices.ix[date][symbol]
                print date, orders.ix[i]['action'], symbol,\
                 'SELL', qty, '@ ', sell_prices.ix[date][symbol], \
                 'REMAINING', portfolio_holdings.ix[date][symbol]\
                  , 'Cash = ', port_value.ix[date]['Cash']

            else :
                if isnan(portfolio_holdings.ix[date][symbol]) :
                    portfolio_holdings.ix[date][symbol] = 0
                portfolio_holdings.ix[date][symbol] -= qty
                port_value.ix[date]['Cash'] -= qty * sell_prices.ix[date][symbol]
                print date, orders.ix[i]['action'], symbol,\
                 'SELL', qty, '@ ', sell_prices.ix[date][symbol], \
                 'REMAINING', portfolio_holdings.ix[date][symbol]\
                  , 'Cash = ', port_value.ix[date]['Cash']

        else:
            print 'Bad order'
            raise

        # ffill holdings and cash from this to the next order date
        if i < len(orders) - 1 :
                date_1 = orders.index[i]
                date_2 = orders.index[i + 1]
                diff = portfolio_holdings.index.searchsorted(date_2)\
                        - portfolio_holdings.index.searchsorted(date_1)
                portfolio_holdings = portfolio_holdings.fillna\
                (method = 'ffill', limit = diff)
                port_value = port_value.fillna\
                (method = 'ffill', limit = diff)

    port_value['Value'] = (sell_prices * portfolio_holdings).sum(axis=1)
    port_value['Total'] = port_value.sum(axis=1)

    return port_value, portfolio_holdings
###############################################################################
# main routine
##############

# initialization
################
print 'Initializing variables\n\n'
data_path = 'D:\\Google Drive\\Python Projects\\PyScripter Projects\\Computational Investing\Data\\'

start_date = dt.datetime(2007,1,1)
end_date = dt.datetime(2013,5,20)

symbols = ['DIA','SPY','IHE','FBT','VDC','MDY','UUP','SHY','EFA','EWC','BND','IEF','VNQ','INP','DBC','VWO','EEB','MYY','TLT','ILF','EPP','EWZ','FXY','FXI']

top_n = 2
leverage = 1.
starting_cash = 100000.

if top_n > len(symbols) :
    print "====== ERROR : top_n must be <= no of symbols!"

# check trading days using assuming SPY date
market_data = get_history(['SPY'], dt.datetime(2000, 1, 1), end_date, data_path)['SPY']['Close']

trading_dates = market_data.index

# make sure start and end are trading dates
start = trading_dates[trading_dates.searchsorted(start_date, side='right')]
end = trading_dates[trading_dates.searchsorted(end_date, side='left')]

# note: ranks => highest = best
transforms = {"d_returns" : {"t_func" : "data[symbol]['Adj Close'].pct_change(periods=1)", "t_close" : "Adj Close", "t_lookback" : 1 ,"t_rank_ascending" : None} ,\
              "perf_20" : {"t_func" : "data[symbol]['Adj Close'].pct_change(periods=20)", "t_close" : "Adj Close", "t_lookback" : 20 ,"t_rank_ascending" : True} ,\
              "perf_62" : {"t_func" : "data[symbol]['Adj Close'].pct_change(periods=62)", "t_close" : "Adj Close", "t_lookback" : 62 ,"t_rank_ascending" : True} ,\
              "vol_20" : {"t_func" : "pd.rolling_std(data[symbol]['d_returns'], 20) * sqrt(252)", "t_close" : "d_returns", "t_lookback" : 20 ,"t_rank_ascending" : False} ,  ## need std of RETURNS!!
             }

max_lookback = np.array([transforms[t_name]['t_lookback'] for t_name in transforms.keys()]).max()

start_extended = trading_dates[list(trading_dates).index(start) - max_lookback]
start_extended
############################################################################
# get data and check it
#######################
print 'Get data and check for bad or incomplete data\n\n'

data = get_history(symbols, start_extended, end, data_path)

# check for incomplete data
for key in data.keys() :
    if data[key].first_valid_index() <> data[key].index.min() :
        print 'WARNING: ',  key, 'only has valid data from ', data[key].first_valid_index()

# need to test for bad data!
for symbol in symbols :
    bad_idx = pd.isnull(data[symbol][data[symbol].index >= data[symbol].first_valid_index()]).any(1).nonzero()[0]
    print symbol, ': bad data len =', len(bad_idx), '===>', bad_idx

# we can just forward fill these
data = data.fillna(method='pad')

# check for bad data again
for symbol in symbols :
    bad_idx = pd.isnull(data[symbol][data[symbol].index >= data[symbol].first_valid_index()]).any(1).nonzero()[0]
    print symbol, ': bad data len =', len(bad_idx), '===>', bad_idx

#############################################################################
# creates a df for each of the transforms
#########################################
print 'Generate strat_data\n\n'

strat_data = {}

for key in list(data.minor_axis) :
    strat_data = dict(strat_data.items() + {key : data.ix[:,:,key]}.items())

# this creates a dictionary entry for each transform
for t_name in transforms.keys():
    for symbol in data.keys():
        data[symbol][t_name] = eval(transforms[t_name]["t_func"])
    vars()[t_name] = pd.DataFrame([[data[symbol][t_name][i]\
                     for symbol in data.keys()]\
                     for i in range(len(data.major_axis))],\
                     index = data.major_axis, columns = data.keys())
    strat_data = dict(strat_data.items() + {t_name:vars()[t_name]}.items())

# need strat_data to include max_lookback dates
strat_data_index = strat_data['Close'].index
strat_data_length = len(strat_data_index)
############################################################################
# create event (re-balance) date
print 'Determine event dates\n\n'

dates = strat_data['Close'].ix[start:end].index  # period-of-interest dates

#===============================================================================
# n = 1   # day of month to re-balance
# rebalance_dates = list([dates[n-1]]) + [dates[i+n-1]\
#                  for i in range(1,len(dates))\
#                   if dates[i].month > dates[i-1].month]
#===============================================================================

# for last trading day of month uncomment

rebalance_dates = [dates[i-1] for i in range(1,len(dates))\
                   if dates[i].month > dates[i-1].month or dates[i].year\
                    > dates[i-1].year ] + list([dates[-1]])

########################################################################
# now need to calculate relative strengths based on algo formula
# best is highest
# only need rs for rebalance dates
print 'Symbol ranks @ rebalance dates\n\n'

rs = pd.DataFrame( [(0.5 * strat_data['perf_62'].rank(axis = 1, ascending = False)\
                    + 0.3 * strat_data['perf_20'].rank(axis = 1, ascending = False)\
                    + 0.2 * strat_data['vol_20'].rank(axis = 1, ascending = True)).ix[i]\
                    for i in rebalance_dates] ,\
                    index=rebalance_dates, columns=data.keys())

# this is to avoid tied ranks - max must NOT BE 0!! (else: LARGE)
rs = pd.DataFrame([rs.ix[i] * 10\
                             + strat_data['perf_62'].ix[i].max()\
                             - strat_data['perf_62'].ix[i]/\
                             strat_data['perf_62'].ix[i].max()\
                             for i in rebalance_dates],\
                            index=rebalance_dates, columns=rs.columns)

# check for bad data
for symbol in symbols :
    bad_idx = pd.isnull(rs[symbol][rs[symbol].index >= rs[symbol]\
            .first_valid_index()]).any().nonzero()[0]
    print symbol, ': bad data len =', len(bad_idx), '===>', bad_idx
# rank symbols according to relative strength
# make 1 the best rank to ease choosing top_n best
ranks = rs.rank(axis = 1, ascending = True)

# may need to check for duplicate ranks?
############################################################################
# portfolio symbols at each rebalance date based on ranking and top_n
print 'top_n symbols @ rebalance dates\n\n'


portfolio_symbols = pd.DataFrame(index=ranks.index, columns=symbols)
for row in range(len(ranks.index)) :
#    print 'row:',row,
    for symbol in ranks.columns:
#        print 'symbol:',symbol,
        if ranks[symbol][row] <= top_n :
            portfolio_symbols.ix[row][symbol] = 1

############################################################################
print 'portfolio weights @ rebalance dates\n\n'

# portfolio weights are determined using Global Min Variance Optimization

#portfolio_weights = optimize(strat_data, rebalance_dates, portfolio_symbols,\
#          lookback=max_lookback,\
#          leverage=leverage)
weights = list([1./top_n]) * len(symbols)


portfolio_weights = pd.DataFrame([weights for i in range(len(rs))],index=portfolio_symbols.index,\
                                 columns=symbols)
portfolio_weights = portfolio_weights * portfolio_symbols
###########################################################################
print 'extract buy/sell dates\n\n'

#sell_px = strat_data['Open'].ix[start:end]
buy_px = strat_data['Close'].ix[start:end]
sell_px = buy_px
# sell price = yesterdays close
#sell_px = strat_data['Adj Close'].shift(1).ix[start:end]

############################################################################
print 'create orders and backtest\n\n'

# backtesting

# create orders for each of the rebalance dates
orders = pd.DataFrame(index=rebalance_dates, columns=['symbol', 'action', 'qty', 'amount'])
# Rebalance1 liquidates and rebalances by weight
# Rebalance2 does not sell shares if in last and rebalances the remainder equally
orders['action'] = 'Rebalance2'

# do backtest
portfolio_values, portfolio_holdings = backtest(100000.0, orders, sell_px, buy_px, portfolio_symbols, portfolio_weights, data_path)

p = portfolio_values.plot()
p.grid(True,linestyle=':')
p.axhline(starting_cash, color='black', lw=1)
show()

metrics = analyze(portfolio_values, data_path, index_ticker='SPY', p_print='Yes')

print '\nBacktest Complete'
