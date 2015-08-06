## firms_by_NASDAQ.py
## I implement downloading security list from NASDAQ, saving and reading the csv file, and 
## databasing with SQLAlchemy into a PostgreSQL database
##   
############################################################################ 
## Copyleft 2015, Ernest Yeung <ernestyalumni@gmail.com>                            
##                                                            
## 20150805
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

import csv
from urlparse import urlparse, parse_qs
import requests
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Numeric, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import collections


iamauser = raw_input("Input your username: ")
if iamauser == "":
    iamauser = "patrickbateman"
password = raw_input("Input your password: ")

engine = create_engine("postgresql://"+iamauser+":"+password+"@localhost/marche")

##################################################
## trial list of urls from nasdaq.com/quotes
##################################################

filename_prefix = "companylist"

trial_urls = [ "http://www.nasdaq.com/screening/companies-by-name.aspx?exchange=NASDAQ&render=download", "http://www.nasdaq.com/screening/companies-by-name.aspx?exchange=AMEX&render=download", "http://www.nasdaq.com/screening/companies-by-name.aspx?exchange=NYSE&render=download" ]

trial_filenames = [ filename_prefix+parse_qs(urlparse(trial_urls[0]).query)['exchange'][0]+'.csv',
                    filename_prefix+parse_qs(urlparse(trial_urls[1]).query)['exchange'][0]+'.csv',
                    filename_prefix+parse_qs(urlparse(trial_urls[2]).query)['exchange'][0]+'.csv' ]

def get_co_csv(url, filename_prefix):
    
    with open(filename_prefix+parse_qs(urlparse(url).query)['exchange'][0]+'.csv',"wb") as f:  # e.g. NASDAQ
        r = requests.get(url)
        f.write(r.content)
        f.close()
    return r

def read_cos_csv(filename):
    """
    read_cos_csv
    cf. http://stackoverflow.com/questions/24662571/python-import-csv-to-list
    """
    f = open(filename,'rb')
    reader = csv.reader(f)
    your_list = list(reader)
    f.close()

    # preprocessing
    # cf. http://stackoverflow.com/questions/3845423/remove-empty-strings-from-a-list-of-strings
    your_list = [ filter(None,row) for row in your_list ] 
    your_list = [[s.strip() for s in row] for row in your_list ]
    return your_list

def check_same_ticker(your_list):
    """
    check_same_ticker
    cf. http://stackoverflow.com/questions/9835762/find-and-list-duplicates-in-python-list
    """
    a = [row[0] for row in your_list ]
    return [item for item, count in collections.Counter(a).items() if count > 1]


########################################
## SQLAlchemy db 
########################################

colsNASDAQ = {
    '__tablename__': 'NASDAQbynasdaq',
    'Symbol'       : Column('Symbol', String, primary_key=True),   
    'Name'         : Column('Name', String),  
    'LastSale'     : Column('LastSale', String),
    'MarketCap'    : Column('MarketCap', String),
    'IPOyear'      : Column('IPOyear', String),
    'Sector'       : Column('Sector', String),
    'industry'     : Column('industry', String),
    'SummaryQuote' : Column('SummaryQuote', String),
    'Market'       : Column('Market', String),
    }

colsAMEX = {
    '__tablename__': 'AMEXbynasdaq',
    'Symbol'       : Column('Symbol', String, primary_key=True),   
    'Name'         : Column('Name', String),  
    'LastSale'     : Column('LastSale', String),
    'MarketCap'    : Column('MarketCap', String),
    'IPOyear'      : Column('IPOyear', String),
    'Sector'       : Column('Sector', String),
    'industry'     : Column('industry', String),
    'SummaryQuote' : Column('SummaryQuote', String),
    'Market'       : Column('Market', String)
    }

colsNYSE = {
    '__tablename__': 'NYSEbynasdaq',
    'Symbol'       : Column('Symbol', String, primary_key=True),   
    'Name'         : Column('Name', String),  
    'LastSale'     : Column('LastSale', String),
    'MarketCap'    : Column('MarketCap', String),
    'IPOyear'      : Column('IPOyear', String),
    'Sector'       : Column('Sector', String),
    'industry'     : Column('industry', String),
    'SummaryQuote' : Column('SummaryQuote', String),
    'Market'       : Column('Market', String)
    }

colsSec = {
    '__tablename__': 'securitiesbynasdaq',
    'id'           : Column('id', Integer, primary_key=True),
    'Symbol'       : Column('Symbol', String),   
    'Name'         : Column('Name', String),  
    'LastSale'     : Column('LastSale', String),
    'MarketCap'    : Column('MarketCap', String),
    'IPOyear'      : Column('IPOyear', String),
    'Sector'       : Column('Sector', String),
    'industry'     : Column('industry', String),
    'SummaryQuote' : Column('SummaryQuote', String),
    'Market'       : Column('Market', String)
    }

##########
## EY : 20150805 I've tried dict.copy to try to construct columns from a single dictionary, but once a class is constructed, the Columns of sqlalchemy inherits the table it belongs to immediately from that first table, and propagates to all related dictionaries; I haven't tried deepcopy, i.e. cols = deepcopy(colsNYSE) then change the tablename, cols['__tablename__'] = 'othercol'
##########

def co_repr(self):
    return "<Security listing(Symbol='%s', Name='%s', LastSale='%s', MarketCap='%s', IPOyear='%s', Sector='%s', industry='%s', Summary='%s'>" % (self.Symbol, self.Name, self.LastSale, self.MarketCap, self.IPOyear, self.Sector, self.industry, self.SummaryQuote) 

Base = declarative_base()

def Row(clsname,base,dict):
    Row=type(str(clsname),(base,),dict)
    return Row

securityNASDAQ = Row("securityNASDAQ", Base, colsNASDAQ )
securityAMEX   = Row("securityAMEX"  , Base, colsAMEX )
securityNYSE   = Row("securityNYSE"  , Base, colsNYSE )
security       = Row("security"      , Base, colsSec )

setattr(securityNASDAQ, '__repr__', co_repr)
setattr(securityAMEX  , '__repr__', co_repr)
setattr(securityNYSE  , '__repr__', co_repr)
setattr(security      , '__repr__', co_repr)

# EY : 20150805 Do this once to create the metadata; otherwise, doing it again, I get these errors:
# 07:26 PM PST update; fix the privileges with psql; test out commands here 
# http://www.cyberciti.biz/faq/howto-add-postgresql-user-account/
#####
# sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server: Connection refused
# Is the server running on host "localhost" (::1) and accepting
# TCP/IP connections on port 5432?
# could not connect to server: Connection refused
# Is the server running on host "localhost" (127.0.0.1) and accepting
# TCP/IP connections on port 5432?
#####
Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()

############################################################
## preprocess csv entries for SQLAlchemy session add_all
############################################################

# l0 = read_cos_csv(trial_filenames[0])

def toSQLfromcsv(filename,Row,market="NASDAQ"):
    """
    toSQLfromcsv = toSQLfromcsv(filename,Row)
    Row is a sqlalchemy DeclarativeMeta
    market is a string that specifies which market the security belongs to; default is "NASDAQ"

    e.g. Examples of USAGE

    toNASDAQ = toSQLfromcsv( trial_filenames[0] , securityNASDAQ )
    toAMEX   = toSQLfromcsv( trial_filenames[1] , securityAMEX, "AMEX" )
    toNYSE   = toSQLfromcsv( trial_filenames[2] , securityAMEX, "NYSE" )

    session.add_all( toNASDAQ )
    session.add_all( toAMEX )
    session.add_all( toNYSE )
    session.commit()

    """
    l = read_cos_csv(filename)
    headers = ["".join(header.split()) for header in l[0]]
    output = []
    for row in l[1:]:
        output.append( Row( Market=market, **dict(zip(headers,row))))
    return output

##### example of building a bigger database
"""
output = []
for file in trial_filenames:
    output1 = toSQLfromcsv(file, security, file[11:].split('.')[0])
    output += output1
    
""" 

