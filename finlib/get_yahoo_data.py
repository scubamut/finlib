#-------------------------------------------------------------------------------
# Name:        get_yahoo_data
# Purpose:
#
# Author:      scubamut
#
# Created:     03/01/2014
# Copyright:   (c) scubamut 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import datetime as dt

def get_yahoo_data(symbol, start, end):

    import pandas as pd

	# set the end date
    y, m, d = str(end).split('-')
    m = str(int(m) - 1)         # months start for 0 on Yahoo!

    # set the start date
    sy, sm, sd = str(start).split('-')
    sm = str(int(sm) - 1)         # months start for 0 on Yahoo!

    url = "http://ichart.finance.yahoo.com/table.csv?s="+symbol+"&d="+ m+ "&e="+ d+ "&f="+ y+ "&g=&a="+ sm+ "&b="+ sd+ "&c="+ sy+ "&ignore=.csv"

    return pd.read_csv(url, index_col='Date',parse_dates=True)

if __name__ == '__main__':

	start = dt.datetime(1990,1,1).date()
	end = dt.datetime.today().date()

	symbol = 'SPY'

	df = get_yahoo_data(symbol, start, end)
	print df[:10]
