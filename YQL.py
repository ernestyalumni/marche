## YQL.py
## I implement downloading of historical prices and other financial data from Yahoo! Finance, saving and reading the csv file, and 
## YQL.py - A wrapper for the Yahoo YQL API; it is based on gurch101's work here:
## cf. https://github.com/gurch101/StockScraper/blob/master/stockretriever.py
## But here I use BeautifulSoup and requests 
##
## from original readme for stockscraper.py
## stockretriever.py
## A self-contained script that retrieves stock information from Yahoo! Finance using YQL
## Usage described @ http://www.gurchet-rai.net/dev/yahoo-finance-yql
##   
############################################################################ 
## Copyleft 2015, Ernest Yeung <ernestyalumni@gmail.com>                            
##                                                            
## 20150812
##                                                                               
## This program, along with all its code, is free software; you can redistribute 
## it and/or modify it under the terms of the GNU General Public License as 
## published by the Free Software Foundation; either version 2 of the License, or   
## (at your option) any later version.                                        
##     
## This program is distributed in the hope that it will be useful,               
## but WITHOUT ANY WARRANTY; without even the implied warranty of              
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 
## GNU General Public License for more details.                             
##                                                                          
## You can have received a copy of the GNU General Public License             
## along with this program; if not, write to the Free Software Foundation, Inc.,  
## S1 Franklin Street, Fifth Floor, Boston, MA                      
## 02110-1301, USA                                                             
##                                                                  
## Governing the ethics of using this program, I default to the Caltech Honor Code: 
## ``No member of the Caltech community shall take unfair advantage of        
## any other member of the Caltech community.''                               
##                                                         
## Donate, and support my other scientific and engineering endeavors at 
## ernestyalumni.tilt.com                                                      
##                          
## Facebook     : ernestyalumni                                                   
## linkedin     : ernestyalumni                                                    
## Tilt/Open    : ernestyalumni                                                    
## twitter      : ernestyalumni                                                   
## youtube      : ernestyalumni                                                   
## wordpress    : ernestyalumni                                                    
##                                                                                  
############################################################################ 

import requests
from bs4 import BeautifulSoup

from base import urlparts

import csv
from urllib2 import urlopen

PUBLIC_API_URL = 'http://query.yahooapis.com/v1/public/yql'
DATATABLES_URL = 'store://datatables.org/alltableswithkeys'
HISTORICAL_URL = 'http://ichart.finance.yahoo.com/table.csv?s='
RSS_URL = 'http://finance.yahoo.com/rss/headline?s='
FINANCE_TABLES = {'quotes': 'yahoo.finance.quotes',
                 'options': 'yahoo.finance.options',
                 'quoteslist': 'yahoo.finance.quoteslist',
                 'sectors': 'yahoo.finance.sectors',
                 'industry': 'yahoo.finance.industry'}

HISTP_URL      = "http://finance.yahoo.com/q/hp"

def executeYQLQuery(yql):
    yqldict = {'q': yql, 'format': 'json', 'env': DATATABLES_URL }
    url = urlparts(PUBLIC_API_URL)
    url.qs = yqldict
    url.mkquery()
    return requests.get( url.urlout() ).json


class YQLQuery(object):
    def execute(self,yql):
        qdict = {'q' : yql , 'format' : 'json', 'env': DATATABLES_URL} 
        xparts = urlparts( PUBLIC_API_URL )
        xparts.qs = qdict
        xparts.mkquery()
        self.rqstrespone = requests.get( xparts.urlout() )

def __format_symbol_list(symbolList):
    return ",".join(["\""+stock+"\"" for stock in symbolList])


def __validate_response(response, tagToCheck):
    quoteInfo = response()['query']['results'][tagToCheck]
    return quoteInfo

def get_current_info(symbolList, columnsToRetrieve='*'):
    """Retrieves the latest data (15 minute delay) for the 
    provided symbols."""

    columns = ','.join(columnsToRetrieve)
    symbols = __format_symbol_list(symbolList)

    yql = 'select %s from %s where symbol in (%s)' \
          %(columns, FINANCE_TABLES['quotes'], symbols)
    response = executeYQLQuery(yql)
#    return response
    return __validate_response(response, 'quote')

def get_historical_info(symbol):
    """Retrieves historical stock data for the provided symbol.
    Historical data includes date, open, close, high, low, volume,
    and adjusted close."""

    yql = 'select * from csv where url=\'%s\'' \
      ' and columns=\"Date,Open,High,Low,Close,Volume,AdjClose\"' \
         % (HISTORICAL_URL + symbol)
    results = executeYQLQuery(yql)
    # delete first row which contains column names
    del results()['query']['results']['row'][0]
    return results()['query']['results']['row']

def get_histPcsv(symbol, startdate ='', enddate=''):
    """
    get_histPcsv - get historical prices .csv
    Rationale - EY : YQL doesn't get all the historical prices-very strange
    """
    HistPurl = urlparts( HISTORICAL_URL )
    if (startdate == '' and enddate == ''):
        HistPurl.qs = {'s': symbol }
        HistPurl.mkquery()

    f = urlopen( HistPurl.urlout()  )
    data = [ row for row in csv.reader(f) ]
    return data

def get_news_feed(symbol):
    """Retrieves the rss feed for the provided symbol."""

    feedUrl = RSS_URL + symbol
    yql = 'select title, link, description, pubDate from rss where url=\'%s\'' % feedUrl
    response = executeYQLQuery(yql)
    if response()['query']['results']['item'][0]['title'].find('not found') > 0:
        raise QueryError('Feed for %s does not exist.' % symbol)
    else:
        return response()['query']['results']['item']


def get_options_info(symbol, expiration='', columnsToRetrieve ='*'):
    """Retrieves options data for the provided symbol."""

    columns = ','.join(columnsToRetrieve)
    yql = 'select %s from %s where symbol = \'%s\'' \
          % (columns, FINANCE_TABLES['options'], symbol)

    if expiration != '':
        yql += " and expiration='%s'" %(expiration)

    response = executeYQLQuery(yql)
    return __validate_response(response, 'optionsChain')


def get_index_summary(index, columnsToRetrieve='*'):
    columns = ','.join(columnsToRetrieve)
    yql = 'select %s from %s where symbol = \'@%s\'' \
          % (columns, FINANCE_TABLES['quoteslist'], index)
    response = executeYQLQuery(yql)
    return __validate_response(response, 'quote')


def get_industry_ids():
    """retrieves all industry names and ids."""

    yql = 'select * from %s' % FINANCE_TABLES['sectors']
    response = executeYQLQuery(yql)
    return __validate_response(response, 'sector')


def get_industry_index(id):
    """retrieves all symbols that belong to an industry."""

    yql = 'select * from %s where id =\'%s\'' \
          % (FINANCE_TABLES['industry'], id)
    response = executeYQLQuery(yql)
    return __validate_response(response, 'industry')


#if __name__ == "__main__":
#    try:
#        print get_current_info(sys.argv[1:])
        #print get_industry_ids()
        #get_news_feed('yhoo')
#    except QueryError, e:
#        print e
#        sys.exit(2)
