#-------------------------------------------------------------------------------
# Name:        get_trading_dates
# Purpose:      to create a list of trading dates (timestamps)
#               for use with Quantopian or Zipline
#
# Author:      scubamut
#
# Created:     16/06/2013
# Copyright:   (c) scubamut 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from zipline.utils import tradingcalendar
import pytz
import datetime as dt

def get_trading_dates(start, end, offset=0):

    trading_dates = list([])

    trading_days= tradingcalendar.get_trading_days(start, end)

    month = trading_days[0].month
    for i in range(len(trading_days)) :
        if trading_days[i].month != month :
            try :
                trading_dates = trading_dates + list([trading_days[i + offset]])
            except :
                raise

            month = trading_days[i].month

    return trading_dates

if __name__ == '__main__':

    start = dt.datetime(2008, 1, 1, tzinfo=pytz.utc)
    end = dt.datetime(2010, 12, 31, tzinfo=pytz.utc)

    trading_dates = get_trading_dates(start, end, offset = -2 )
    print trading_dates

