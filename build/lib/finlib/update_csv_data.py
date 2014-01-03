#-------------------------------------------------------------------------------
# Name:         update_csv_data
# Purpose:      get history data from Yahoo 'til today
#               If csv exists, refresh and save
#               If no csv, get from web and save to csv
#               Nothing returned
#
# Calling:      update_csv_data(symbols, start, end, data_path)
#               NOTE: date format datetime.datetime, must be trading days
#               symbols = symbol list
#
# Author:       Dave Gilbert
#
# Created:      21/05/2013
# Copyright:    (c) D. Gilbert 2013
# Licence:      <your licence>
#-------------------------------------------------------------------------------
import datetime as dt
import pandas as pd
import pandas.io.data as web

def update_csv_data(symbols, data_path):

    # set start way back if no saved data yet
    start = dt.datetime(1990,1,1)
    end = dt.datetime.today().date()

    for ticker in symbols:
        print ticker,
        try:
            #see if csv data available
            data = pd.read_csv(data_path + ticker + '.csv',\
                                index_col='Date', parse_dates=True)
        except:
            #if no csv data, create an empty dataframe
            print 'No saved data..',
            data = pd.DataFrame(data=None, index=[start])

        if data.empty == False :
            start = data.index.max().date()

        #check if there is data for the start-end data range

        if data.index[-1].toordinal() < end.toordinal() - 3 :

            print 'Get Yahoo data.. ',
            try:
                new_data = web.get_data_yahoo(ticker, start, end)
            except:
                print 'Download failed.. '
            if new_data.empty==False:
                if data.empty==False:
                    try:
                        ticker_data = data.append(new_data)\
                        .groupby(level=0, by=['rownum']).last()
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
        else:
            print 'OK.. '
            status = 'OK'
        pass

    return

def main():

    data_path = 'D:\\Google Drive\\Python Projects\\PyScripter Projects\\Computational Investing\Data\\'

    symbols = ['IHE', 'DIA', 'VWO', 'GLD']

    update_csv_data(symbols, data_path)

if __name__ == '__main__':
    main()
