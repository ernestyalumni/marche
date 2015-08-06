## apres_firms_by_NASDAQ.py
## I implement downloading security list from NASDAQ, saving and reading the csv file, and 
## databasing with SQLAlchemy into a PostgreSQL database
## This file is for AFTER (apres) you put the data into the postgreSQL database 
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

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from firms_by_NASDAQ import engine, securityNASDAQ, securityAMEX, securityNYSE, security

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

########################################
## Examples of query; example queries
########################################

"""
for instance in session.query(security).order_by(security.Symbol): print instance

qAAPL = session.query(security).filter(security.Symbol == 'AAPL')
qAAPL.scalar()

qAAPL.all()[0].Market
print [ getattr(qAAPL.all()[0], str(m.key) ) for m in security.__table__.columns ]

for m in securityNYSE.__table__.columns: print m, m.key
"""

