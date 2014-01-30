#-------------------------------------------------------------------------------
# Name:         get_history
# Purpose:      get history data from source (Yahoo or QSTK).
#               If csv exists, refresh and save, if necessary
#               If no csv, get from web and save to csv
#               Return pandas datapanel, ascending dates
#
# Calling:      get_history(symbols, start, end, data_path)
#               NOTE: date format datetime.datetime, must be trading dates
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

def get_history(symbols, start, end, data_path):

    symbols_ls = list(symbols)
    for ticker in symbols:
        print ticker,
        try:
            #see if csv data available
            data = pd.read_csv(data_path + ticker + '.csv', index_col='Date', parse_dates=True)
        except:
            #if no csv data, create an empty dataframe
            data = pd.DataFrame(data=None, index=[start])

        #check if there is data for the start-end data range

        if start.toordinal() < data.index[0].toordinal() \
                             or end.toordinal() > data.index[-1].toordinal():

            print 'Refresh data.. ',
            try:
                new_data = web.get_data_yahoo(ticker, start, end)

                if new_data.empty==False:
                    if data.empty==False:
                        try:
                            ticker_data = data.append(new_data).groupby(level=0, by=['rownum']).last()
                        except:
                            print 'Merge failed.. '
                    else:
                        ticker_data = new_data
                    try:
                        ticker_data.to_csv(data_path + ticker + '.csv')
                        print ' UPDATED.. '
                    except:
                        print 'Save failed.. '
                else:
                    print 'No new data.. '
            except:
                print 'Download failed.. '
                # remove symbol from list
                symbols_ls.remove(ticker)
        else:
            print 'OK.. '
        pass

    pdata = pd.Panel(dict((symbols_ls[i], pd.read_csv(data_path + symbols_ls[i] + '.csv',\
                     index_col='Date', parse_dates=True).sort(ascending=True)) for i in range(len(symbols_ls))) )


    return pdata.ix[:, start:end, :]

if __name__ == '__main__':

    data_path = 'G:\\Google Drive\\Python Projects\\PyScripter Projects\\Computational Investing\\Data\\'

    # these must be trading dates
    start_date = '1/1/1992'
    end_date = '4/9/2012'

    start = dt.datetime.strptime(start_date, '%d/%m/%Y').date()
    end = dt.datetime.strptime(end_date, '%d/%m/%Y').date()

#    market_index = get_history(['SPY', 'EEM'], start, end, data_path).ix[:,:,'Adj Close']
    data = get_history(['VFINX', 'VEURX', 'VPACX', 'VGSIX', 'VBMFX', 'FSHBX', 'VGPMX'], start,  end, data_path)
    print
#    print market_index.info
