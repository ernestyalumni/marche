## fun_with_quandl.py
## I implement some fun stuff using Quandl information, already downloaded and persisted
## locally 
##   
############################################################################ 
## Copyleft 2015, Ernest Yeung <ernestyalumni@gmail.com>                            
##                                                            
## 20150908
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

from firms_by_NASDAQ import engine
from quandl_to_SQL import SRC, DataSet

import sqlalchemy
from sqlalchemy.orm import sessionmaker

import pandas
import pandas as pd
from pandas.tools.plotting import lag_plot

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter, date2num
import matplotlib.ticker as ticker

import pywt
import statsmodels
import statsmodels.api as sm

import numpy as np

SUBDIR = './rawdata/quandl/'

Session = sessionmaker(bind=engine)
session = Session()

#####################################################################################
##### Examples of USAGE
#####################################################################################

session.query(SRC).filter(SRC.src.match("YALE")).first().datasets
for ds in session.query(SRC).filter(SRC.src.match("YALE")).first().datasets: print ds.code, ds.name

yaleds = session.query(SRC).filter(SRC.src.match("YALE")).first().datasets

code = yaleds[12].code

code_editted = code.replace('/','__')

yspper10y = pandas.read_pickle(SUBDIR+code_editted)

# numpy ndarray of datetime
yspper10y.index.to_pydatetime()

# use matplotlib.dates's date2num
date2num( yspper10y.index.to_pydatetime() )

# get the values as a numpy array with values, after choosing which column by a Python dictionary manner
yspper10y['Value'].values

################################################################# 
## fun with wavelets
################################################################# 

yspper10ydwted = pywt.dwt( yspper10y['Value'].values, "haar", mode="cpd")

# try different levels
yspper10dwtedcoeffs = pywt.wavedec(yspper10y['Value'].values, 'haar', level=3)

# try maximum wavelent decomposition
yspper10dwtedcoeffs = pywt.wavedec(yspper10y['Value'].values, 'haar')



################################################################# 
## fun with lag_plots
################################################################# 

lag_plot(yspper10y)
plt.title("Lag plot of 1-year lag of "+yaleds[12].name, fontsize=12)

################################################################################ 
##### Is the U.S. stock market overvalued?
################################################################################ 

################################################################################ 
### Is the U.S. S&P 500 Price-to-Earnings (PE) ratio too expensive right now?
################################################################################

# EY : 20150910 in pandas, for a DataFrame, .plot() methods serves a "wrapper" for matplotlib's plt, see the pandas tutorial for Plotting
fig = yspper10y.plot().figure
fig.suptitle( yaleds[12].name,fontsize=14,fontweight='bold')
ax = fig.add_subplot(111)
ax.set_ylabel(yaleds[12].colname.split(',')[1] +' ;  P/E ratio')
ax.set_xlabel(yaleds[12].colname.split(',')[0])
ax.text(-50,40,"frequency: "+yaleds[12].freq)
ax.text(-50,38,"Quandl CODE: "+yaleds[12].code)
ax.text(-50,36, "Source: " +yaleds[12].desc,style='italic' )
ax.grid(True,which='minor',axis='both')

# max value
yspper10y.max() # 42.549083, 2000-12-31

# min value
yspper10y.min() # Value    5.288354

# Last value
yspper10y.index[-1] # Timestamp('2013-12-31 00:00:00')
yspper10y['Value'][-1] # 21.171178848130001

# Wavelet decomposition at level 2
yspewcoeffs2 = pywt.wavedec(yspper10y['Value'].values, 'haar', level=2)

# get the matching dates, by slicing the numpy array, skipping over, or changing the interval
yspper10y.index.to_pydatetime()[::2]
yspper10y.index.to_pydatetime()[::4]

# c_A2 coefficients 
plt.plot( yspper10y.index.to_pydatetime()[::4] , yspewcoeffs2[0] )
plt.title("c_A2 Haar wavelet level 2 decomposition approximation coefficient of "+yaleds[12].name)
plt.ylabel("c_A2")
plt.grid(True,which='minor')

# c_D2 coefficients 
plt.plot( yspper10y.index.to_pydatetime()[::4] , yspewcoeffs2[1] )
plt.title("c_D2 Haar wavelet level 2 decomposition detail coefficient of "+yaleds[12].name, fontsize=12)
plt.ylabel("c_D2")
plt.grid(True)

# c_D2 coefficients 
plt.plot( yspper10y.index.to_pydatetime()[::2] , yspewcoeffs2[2] )
plt.title("c_D1 Haar wavelet level 2 decomposition detail coefficient of "+yaleds[12].name, fontsize=12)
plt.ylabel("c_D1")
plt.grid(True)
