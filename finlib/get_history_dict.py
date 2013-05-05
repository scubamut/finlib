#-------------------------------------------------------------------------------
# Name:         get_history_dict
# Purpose:      get history data from source (Yahoo or QSTK).
#               If csv exists, refresh and save, if necessary
#               If no csv, get from web and save to csv
#               Return dictionary of pandas dataframes, ascending dates
#               {<ticker>: DF, .......}
#
# Calling:      get_history_dict(symbols, start, end, data_path)
#               NOTE: date format datetime.datetime, must be trading days
#               symbols = symbol list
#
# Author:       Dave Gilbert
#
# Created:      14/04/2013
# Copyright:    (c) D. Gilbert 2013
# Licence:      <your licence>
#-------------------------------------------------------------------------------
import datetime as dt
import pandas as pd
import pandas.io.data as web

def get_history_dict(symbols, start, end, data_path):

    for ticker in symbols:
        print ticker,
        try:
            #see if csv data available
            data = pd.read_csv(data_path + ticker + '.csv',\
                                index_col='Date', parse_dates=True)
        except:
            #if no csv data, create an empty dataframe
            data = pd.DataFrame(data=None, index=[start])

        #check if there is data for the start-end data range

        if data.index[-1].toordinal() <= end.toordinal() :

            print 'Refresh data.. ',
            try:
                new_data = web.get_data_yahoo(ticker, start, end)
            except:
                print 'Download failed.. ',
            if new_data.empty==False:
                if data.empty==False:
                    try:
                        ticker_data = data.append(new_data)\
                        .groupby(level=0, by=['rownum']).last()
                    except:
                        print 'Merge failed.. ',
                else:
                    ticker_data = new_data
                try:
                    ticker_data.to_csv(data_path + ticker + '.csv')
                    print ' UPDATED.. ',
                except:
                    print 'Save failed.. ',
            else:
                print 'No new data.. ',
        else:
            print 'OK.. ',
        pass

    pdata = dict((symbols[i], pd.read_csv(data_path + symbols[i] + '.csv',\
                     index_col='Date', parse_dates=True).sort(ascending=True)\
                  .ix[start:end]) for i in range(len(symbols)))


    return pdata

if __name__ == '__main__':

    data_path = 'G:\\Python Projects\\Computational Investing\\Data\\'

    start_date = '3/1/2011'
    end_date = '30/12/2011'

    start = dt.datetime.strptime(start_date, '%d/%m/%Y').date()
    end = dt.datetime.strptime(end_date, '%d/%m/%Y').date()

    market_index = get_history_dict(['SPY', 'EEM'], start, end, data_path)

    print
    print  market_index.items()
