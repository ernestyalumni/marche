## quandl_to_SQL.py
## I implement downloading of quandl data, and saving it (i.e. persisting it) in a SQL database.  
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

import Quandl
from collections import namedtuple

from decimal import Decimal
from datetime import datetime
import re
import os

import pandas

import sqlalchemy
from sqlalchemy import inspect, Column, Date, Integer, Numeric, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

from firms_by_NASDAQ import engine, Base

AUTHTOKEN = "1-BSwozB_-bNApxsgRMg" # your authentication token here (look up your API-key)

def all_dbmetafrmSRC(pglmt=10000,src="YALE", authtkn=AUTHTOKEN):
    """
    all_dbmetafrmSRC = all_dbmetafrmSRC(pglmt=10000,src="YALE",authtkn=AUTHTOKEN)
    all_dbmetafrmSRC, i.e. all database Metadata from a Source, returns all the "metadata", the information describing a databse, for all databases from a single source, specified by a string that is the Quandl code

    INPUTS:
    int pglmt: (default=10000), page numberS to search
    str sre: (default="YALE", chosen as an example), the Quandl code for the SOURCE or "src" to search from
    str authtkn: (default="AUTHTOKEN", that's globally declared at the beginning of the .py code), your authentication code with Quandl, you should find that under API-key in your Quandl account and copy and paste that into the code
    """
    metalst = []
    counter = 1
    while (counter <= pglmt):
        resp = Quandl.search(query="*",source=src,page=counter,authtoken=authtkn)
        if len(resp) != 0:
            metalst = metalst + resp
            counter += 1
        else:
            break
    if counter > pglmt:
        print "Counter limit, pglmt, was reached; try a higher pglmt, i.e. page limit \n"

    return metalst

def getfrmSRC(metalst):
    """
    getfrmSRC = getfrmSRC(src="YALE/SP_PER10Y")
    get from Quandl Code a list of database data as a numpy recarray

    INPUTS:
    list metalst: this is the result from all_dbmetafrmSRC, a list of dictionaries

    EXAMPLES of USAGE
    Ylst = all_dbmetafrmSRC()
    getfrmSRC(Ylst)
    """
#    DataTabletuple = namedtuple('DataTable',['headers','data'])
#    data = [ DataTabletuple(db['colname'], Quandl.get( db['code'],returns="numpy")) for db in metalst ]
    data = [Quandl.get( db['code'],returns="numpy") for db in metalst]
    return data

###################################
##### Yale Department of Economics
##### (35 datasets)
###################################

'''
EXAMPLES of USAGE
Yalelist = Quandl.search(query="*",source="YALE",page=1,authtoken=AUTHTOKEN)
len(Yalelist) # 35
'''

################################################################################
########## SQLAlchemy db
################################################################################

class SRC(Base):
    __tablename__ = 'quandl_source'
    id = Column('uid',Integer,primary_key=True)
    src = Column("src",String,unique=True)
    def __repr__(self):
        return "<__tablename__='%s', Source='%s'>" % (self.__tablename__,self.src)

class DataSet(Base):
    __tablename__ = 'DataSet'
    freq = Column('freq',String)
    code = Column('code',String,primary_key=True)
    colname = Column('colname',String)
    name = Column('name',String)
    desc = Column('desc',String)
    
    src_src = Column(String,ForeignKey('quandl_source.src'))
    src = relationship("SRC", backref=backref('datasets') )

    def __repr__(self):
        return "<DataSet(frequency='%s', Quandl CODE='%s', Name='%s', Description='%s', Columns='%s'>" % (self.freq, self.code, self.name, self.desc, self.colname)

def Row(clsname,base,dict):
    Row=type(str(clsname),(base,),dict)
    return Row
                       
def build_quandl_Data(data, tablename):
    """
    build_quandl_Data
    build_quandl_Data first builds a dictionary of SQLalchemy Columns that match the type of the data retrieved from Quandl (retrieved as a numpy recarray)
    Then it returns a SQLAlchemy class that maps each row data to a Table

    INPUTS:
    REMOVED x- list colname: this is a Python list of strings, that are the column names of a datatable 
    e.g. [u'Year', u'S&P Composite', u'Dividend', u'Earnings', u'CPI', u'Long Interest Rate', u'Real Price', u'Real Dividend', u'Real Earnings', u'Cyclically Adjusted PE Ratio']
    numpy.core.records.recarray data: this is a numpy recarray of data, be careful that there can be null values 
    EY: 20150909 numpy's recarray is great because you get the name of the columns AND the types in a neat (i.e. clear and clean) format

    str tablename: name of the table as a string, I used the code as the table name
    sqlalchemy.ext.declarative.api.Base base : instance of a sqlalchemy Base

    EXAMPLES of USAGE:
    ylst = all_dbmetafrmSRC()
    ydata1 = Quandl.get( ylst[1]['code'],returns="numpy")
    build_quandl_Data(ydata1, ylst[1]['code'] , Base)
    """

    datadtyp     = data.dtype
    datacolnames = datadtyp.names
    tablename_editted = tablename.replace('/','__')

    
    coltypdict = { '__tablename__' : tablename_editted }
    for i in range(len(datacolnames)):        
        # This makes a string that is suitable to be used a key in a dictionary (only alphanumeric characters, no special characters, no spaces)
        colsqlname = "".join(re.findall("[a-zA-Z0-9]+", (datacolnames[i].replace(' ',''))) )
        if (datadtyp[i].kind == 'f') or (datadtyp[i].type == float) or (datadtyp[i].name.find("float") >= 0): 
            coltypdict.update({colsqlname:Column( datacolnames[i], Numeric)})
        elif (datadtyp[i].kind == 'O') or (datacolnames[i]=='Year') or (datacolnames[i]=='Month') or (datacolnames[i]=='Day') or (datacolnames[i]=='Date') or (datadtyp[i].name.find("object")>=0):
            coltypdict.update({colsqlname:Column( datacolnames[i], Date,unique=True)})
        elif (datadtyp[i].kind=='i') or (datadtype[i].name.find("int")>=0):
            coltypdict.update({colsqlname:Column( datacolnames[i], Integer)})
        else:
            print "There was a problem in determining the column type (???)\n"
            break
    
    coltypdict.update({'code':Column('code',String,ForeignKey(DataSet.code))})
    coltypdict.update({'dataset':relationship("DataSet")})
    coltypdict.update({'id':Column('id',Integer,primary_key=True)})
    

    def co_repr(self):
        return "<Data point in code='%s' of Table name='%s'>" % (self.code, self.__tablename__ )
    coltypdict.update({'__repr__': co_repr})
    datacls = Row(tablename,Base,coltypdict)

    headers = ["".join(re.findall("[a-zA-Z0-9]+", (colname.replace(' ','')))) for colname in datacolnames]
    
    data_to_SQL = [datacls(code=tablename,**dict(zip(headers,row))) for row in data]
    
    return datacls, data_to_SQL
    

def toSQLfrmSRC(srcname="YALE"):
    srcpt = SRC(src=srcname)
    dblst = all_dbmetafrmSRC(src=srcname)
    for lst in dblst:
        if type(lst['colname']) == type([]):
            lst['colname'] = ",".join(lst['colname'])
    DataSetlst = [DataSet(src_src=srcname, **lst) for lst in dblst]

#    dataclses = []
#    for lst in dblst:
#        datafoo = Quandl.get(lst['code'],authtoken=AUTHTOKEN,rows=1,returns="numpy")
#        datacls, foodata = build_quandl_Data(datafoo, lst['code'])
#        dataclses.append(datacls)

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(srcpt)
    session.add_all(DataSetlst)
    session.commit()
    session.close()

    return dblst

def getasave_topanda(code,src,dirout='./rawdata/quandl/'):
    """
    getasave_toh5 = gateasave_toh5(code,dirout='./rawdata/quandl/')
    get and save into HDF5

    INPUTS:
    str code: this is a Quandl CODE for a dataset
    str src: the Quandl Source name, e.g. "YALE"
    str dirout: this is the directory where you want to put it
    """
    if not os.path.exists(dirout):
        os.makedirs(dirout)
    Qdata = Quandl.get(code,authtoken=AUTHTOKEN) # returns a panda DataFrame

    code_editted = code.replace('/','__')
    Qdata.to_pickle(dirout+code_editted)

    return Qdata

def get_all_quandl_datasets(srcname="YALE"):
    Session = sessionmaker(bind=engine)
    session = Session()
    datasetinfo = session.query(DataSet).filter(DataSet.src_src.match(srcname)).all()
    for pt in datasetinfo:
        getasave_topanda(pt.code,srcname)
    session.close()
    return srcname


def build_all_frmSRC(srcname="YALE"):
    toSQLfrmSRC(srcname)
    get_all_quandl_datasets(srcname)
    return srcname



if __name__ == "__main__":
    choice1st = raw_input("Do you want to build a database of datasets from a source for the first time? Type 'yes' with no quotation marks; otherwise, type any other key(s)")
    if choice1st == 'yes':
        srcname = raw_input("Type in, in caps (capitalized letters), the name of the source")
        build_all_frmSRC(srcname)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    
        

''' DEAD CODE
    f = h5py.File(dirout+src+".hdf5", "w")
    f.create_dataset(code,data=Qdata)
    f.close()

tablename_editted = tablename.replace('/','__')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(srcpt)
    session.add_all(DataSetlst)
    session.commit()
    session.close()
#    dblstsql = []
    for lst in dblst:
        dataset = Quandl.get(lst['code'],authtoken=AUTHTOKEN, returns="numpy")
        #base_datatbls = declarative_base()
        datacls, data_to_SQL = build_quandl_Data(dataset, lst['code'])        

#        DataTableSQLtuple = namedtuple('DataTableSQLtuple',['datacls','data_to_SQL'])
#        dblstsql.append( DataTableSQLtuple( datacls, data_to_SQL ) )
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add_all(data_to_SQL)
        print "Adding '%s'" % lst['code']
        session.commit()
        session.close()
    return dblst
'''

                       
