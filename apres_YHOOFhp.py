## apres_YHOOFhp.py
## I implement downloading of historical prices and other financial data from Yahoo! Finance, 
## saving and reading the csv file, and saving it (i.e. persisting it) in a SQL database.  
## You run this after YHOOF_toSQL.py and the SQL database of YHOO Finance Historical Prices is 
## created.  
##   
############################################################################ 
## Copyleft 2015, Ernest Yeung <ernestyalumni@gmail.com>                            
##                                                            
## 20150831
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
from firms_by_NASDAQ import engine, security, Symbole
from YHOOF_toSQL import Base, YHOOF_DayQuote, insc_SymbHP_daterange
from YHOOF_toSQL import YHOOF_HISTP_datapt as YfHP_pt

import sqlalchemy
from sqlalchemy import func 
from sqlalchemy.orm import sessionmaker 

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter

from datetime import datetime

import urllib2
import httplib

import sys
import time

##############################
## SQLAlchemy implementations
##############################

Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()

################################################################################
### Updating the SQL database of Historical Prices from Yahoo! Finance
################################################################################

def quick_update_HP():
    start0 = time.clock()
    lastdate = session.query(func.max(YfHP_pt.Date)).filter(YfHP_pt.Symbol.match("AAPL")).first()
    end0 = time.clock()
    print "Querying SQL database for last date took this long: ", (end0-start0)*10000

    lastdate = lastdate[0]
    presentdate = datetime.today().date()
    if len(get_histPcsv("AAPL", str(lastdate), str(presentdate))) <= 2:
        print "Database is updated with all current historical prices from Yahoo! Finance \n"
        return 0 
    else:
        targetlst = session.query(Symbole).all()

        start1 = time.clock()
        for ticker in targetlst:
            try:
                output = insc_SymbHP_daterange( ticker.symbole,str(lastdate),str(presentdate))
                session.add_all(output)
                print "Adding %s to session" % ticker
                session.commit()
                
                end1 = time.clock()
                print "Adding into SQL database took this long: ", (end1 - start1)*10

            except urllib2.HTTPError:
                print "Not here: %s" % ticker    

            except httplib.IncompleteRead as e:
                print "Incomplete Read (???): %s" % ticker.symbole

            except sqlalchemy.exc.ProgrammingError as e:
                print output
                raise e 
                
        return output


################################################################################
### Examples of (basic) queries
################################################################################

# Get the entire time series for a single stock, like AAPL, ordered by Date
# it takes about 2 minutes
'''
qAAPL = session.query(YfHP_pt).filter(YfHP_pt.Symbol.match("AAPL")).order_by(YfHP_pt.Date)
qAAPL = qAAPL.all()
'''

################################################################################
### Examples of (basic) plotting
################################################################################

# Plot price vs. time (matplotlib deals with turning a date into a number)
'''
qAAPLdates = [matplotlib.dates.date2num( pt.Date ) for pt in qAAPL ]
qAAPLAdjClose = [pt.AdjClose for pt in qAAPL]
qAAPLVol      = [pt.Volume for pt in qAAPL]
qAAPLClose    = [pt.Close for pt in qAAPL]
qAAPLLow      = [pt.Low for pt in qAAPL]

# cf. http://stackoverflow.com/questions/7733693/matplotlib-overlay-plots-with-different-scales
fig, ax = plt.subplots()
axes = [ax, ax.twinx()]
axes[0].plot_date(qAAPLdates, qAAPLAdjClose, '-',linewidth=3,color="green")  
axes[1].plot_date(qAAPLdates, qAAPLVol,'+',linewidth=1,color="blue")
fig.suptitle('AAPL, Adjusted Close in green, Volume in blue', fontsize=11)
plt.show()

# Plot the Close and Low for the last 60 trading days, making the same scale:
fig, ax = plt.subplots() 
axes = [ax, ax.twinx()]
axes[0].plot_date(qAAPLdates[-300:], qAAPLClose[-300:], 'o',linewidth=2, color="green")
axes[1].plot_date(qAAPLdates[-300:], qAAPLLow[-300:],'+',linewidth=2,color="blue")
axes[0].set_ylim((80.0,140.0))
axes[1].set_ylim((80.0,140.0))
fig.suptitle('AAPL, Close in green, Low in blue', fontsize=11) 
fig.show()
'''

if __name__ == "__main__":
    choice = raw_input("Do you want to update the SQL database of historical prices from Yahoo! Finance? If so, type 'yes' with no quotation marks; otherwise, type or enter any other character: ")
    if choice == 'yes':
        quick_update_HP()

    print "Here's what's available to use (do sys.modules[__name__].__dict__.keys() ): \n "
    for key in sys.modules[__name__].__dict__.keys(): print key
    print "Remember to close the session by running session.close() !!! \n "
