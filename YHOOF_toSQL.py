## YHOOF_toSQL.py
## I implement downloading of historical prices and other financial data from Yahoo! Finance, saving and reading the csv file, and saving it (i.e. persisting it) in a SQL database
## 
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

from YQL import get_histPcsv

from decimal import Decimal
from datetime import datetime

import sqlalchemy
from sqlalchemy import create_engine, Column, Date, Integer, Numeric, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

from firms_by_NASDAQ import engine, security, Symbole, Base

import csv
import os
import urllib2
import time # to time functions, seeing how long it takes to download all historical prices

def ColumnDate(date):
    if date != 'N/A' and date != 'NULL':
        return datetime.strptime(date, '%Y-%m-%d').date()  # this is a Python date object
    else:
        return None

def ColumnDecimal(value):
    if value != 'N/A' and value != 'NULL':
        try:
            return Decimal(value)
        except decimal.InvalidOperation:
            return None
    else:
        return None

def ColumnInt(value):
    if value != 'N/A' and value != 'NULL':
        try:
            return int(value)
        except ValueError:
            return None
    else:
        return None
            
YHOOF_HISTP_headers = {'Date'  : ColumnDate, 
                       'Open'  : ColumnDecimal,
                       'High'  : ColumnDecimal,
                       'Low'   : ColumnDecimal,
                       'Close' : ColumnDecimal,
                       'Volume': ColumnInt,
                       'Adj Close': ColumnDecimal }
    
def YHOOF_DayQuote(header,row, dict=YHOOF_HISTP_headers):
    return [dict[key](value) for (key, value) in zip(header,row)]
    
def YHOOF_HistP_csv_to_SQLprep(symbol, has_header=True):
    data = get_histPcsv( symbol )
    if has_header:
        header = data[0]
        del data[0]
    data = [YHOOF_DayQuote(header,row) for row in data ] 
    data = [row + [symbol,] for row in data ]
    return data

##############################
## SQLAlchemy implementations
##############################


class YHOOF_HISTP_datapt(Base):
    """
    This stackoverflow question and answer helped alot to understanding the 1-to-many relationship established
    """
    __tablename__ = 'YHOOF_HISTP'    

    id           = Column('id', Integer, primary_key=True)
    Symbol       = Column('Symbol', String, ForeignKey(Symbole.symbole))
    Date         = Column('Date', Date)
    Open         = Column('Open',Numeric)
    High         = Column('High',Numeric)
    Low          = Column('Low',Numeric)
    Close        = Column('Close',Numeric)
    Volume       = Column('Volume',Integer)
    AdjClose     = Column('AdjClose',Numeric)

    symbole = relationship("Symbole",backref=backref('timeseries',order_by=Date))

    def __repr__(self):
        return "<Time-series data(id='%s', Symbol='%s', Date='%s', Open='%s', High='%s', Low='%s', Close='%s', Volume='%s', AdjClose='%s'>" % (self.id, self.Symbol, self.Date, self.Open, self.High, self.Low, self.Close, self.Volume, self.AdjClose)


Base.metadata.create_all(engine)


def insc_Symbol_toSQL(symbol):    # inscrire
    """
    insc_Symbol_toSQL = insc_Symbol_toSQL(symbol)
    """
    data=YHOOF_HistP_csv_to_SQLprep(symbol)
    headers=["Date","Open","High","Low","Close","Volume","AdjClose"]
    output =[]
    for row in data:
        output.append( YHOOF_HISTP_datapt(Symbol=symbol, **dict(zip(headers,row))) )
    return output

Session = sessionmaker(bind=engine)
session = Session()

########################################
## EY : 20150813 
## At this point, there are 2 ways to go: download all symbols in 
## session.query(Symbole).all()
## or download a "few" at a time.  
## Right now, I only have a Mid-2011 MacBook Air and Time-Warner Cable so downloading all the symbols at a time might be a problem.  Also, I am concerned with pinging Yahoo! Finance too many times in 1 session.  I'll present both ways.  
########################################

##################################################
## Get all historical prices for symbols available
##################################################

def getasave_tocsv(ticker,dirout='./rawdata/YHOOFHISTP/'):
    if not os.path.exists(dirout):
        os.makedirs(dirout)
    data = get_histPcsv(ticker)
    with open(dirout+ticker+'_YHOOF_HISTP'+'.csv', "wb") as f:
        writer = csv.writer(f)
        writer.writerows(data)
    return data

def buildallYHOOHISTP_1st():
    """
    buildallYHOOHISTP_1st = buildallYHOOHISTP_1st()
    buildallYHOOHISTP_1st builds the SQL database of all Yahoo! Finance Historical Prices 
    for the first time (i.e. run this the first time)
    """
    subdir = './rawdata/YHOOFHISTP/'

    targetlst = session.query(Symbole).all()
    start0 = time.clock()
    for ticker in targetlst:
        try:
            getasave_tocsv(ticker)
            print "%s obtained" % ticker
        except urllib2.HTTPError:
            print "Not here: %s" % ticker
    end0 = time.clock()
    print "Downloading took this long: ", (end0-start0)/1000.

    savedlst = os.listdir(subdir)
    start1 = time.clock()
    for fname in savedlst:
        print "Opening : %s" % fname
        ticker = fname.split('_')[0]
        f = open( subdir+fname,'rb')
        reader = csv.reader(f)
        data = list(reader)
        headers = data[0]
        del data[0]
        data = [YHOOF_DayQuote(headers,row) for row in data]
        data = [row+[symbol,] for row in data]
        
        headers = [header.replace(' ','') for header in headers]
        output = []
        for row in data:
            output.append( YHOOF_HISTP_datapt(Symbol=ticker,**dict(zip(headers,row))) )
        session.add_all(output)
    end1 = time.clock()
    print "Adding into SQL database took this long: ", (end1 - start1)/1000
    print "\n Do session.commit() to commit these changes to the SQL database \n"
    return 0 



            


#####
## The follow 2 functions had taken too much time:

"""
def getallYHOOHISTP_lst():

#    getallYHOOHISTP_lst = getallYHOOHISTP_lst()

    start = time.clock()
    dataout = []
    targetlst = session.query(Symbole).all()
    for ticker in targetlst:
        try:
            datain = insc_Symbol_toSQL(ticker)
            dataout.append( datain )
            print "%s obtained" % ticker
        except urllib2.HTTPError:
            print "Not here: %s" % ticker
    end = time.clock()
    print "It took this long: ", (end-start)/1000.
    return dataout

def buildallYHOOHISTP_1st():

#    buildallYHOOHISTP_1st = buildallYHOOHISTP_1st()
#    buildallYHOOHISTP_1st builds the SQL database of all Yahoo! Finance Historical Prices 
#    for the first time (i.e. run this the first time)

    start = time.clock()
    dataout = getallYHOOHISTP_lst()
    session.add_all(dataout)
    session.commit()
    end = time.clock()
    print "It took this long: ", (end-start)/1000.
    return dataout
"""


# I'll persist the short list of symbols with .csv

def create_short_list(stcklst, filename='YHOOF_shortlst.csv' ):
    with open(filename,'wb') as csvfile:
        stkswriter = csv.writer(csvfile, delimiter=' ')
        stkswriter.writerow(stcklst)
        csvfile.close()
        return stcklst

def read_short_list(filename='YHOOF_shortlst.csv'):
    with open(filename,'rb') as csvfile:
        stksreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        output = []
        for row in stksreader:
            output.append( row )
        csvfile.close()
        return output

def insc_Symbols_toSQL(lst):
    """
    Example of usage
    """
    outputlst = []
    for symbol in lst:
        outputlst = outputlst + insc_Symbol_toSQL(symbol)
    return outputlst





if __name__ == "__main__":
    choice = raw_input("Do you want to build the SQL database of all Yahoo! Finance Historical Prices for the FIRST time? If so, type 'yes' with no quotation marks; otherwise, type or enter any other character: ")
    if choice =='yes':
        buildallYHOOHISTP_1st()
