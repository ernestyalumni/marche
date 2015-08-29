## base.py
## I implement web scraping i.e. screen scraping with these "base" or elementary functions and classes
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

from urllib import urlencode
from urlparse import urlparse, urlunparse, parse_qs, parse_qsl, urljoin

class urlparts(object):
    """
    urlparts - url in parts
    urlparts : the rationale for this class is that we need a Python class object that "wraps" up the stuff from urllib, urlencode, which takes a dictionary and puts it together into a string, which is the url address, and
    urlparse, putting into a class urlparse, urlunparse to put it back together
      and from urlparse, parse_qsl, which deals with parsing queries

    __init__ for this deals with the different ways to fix up the url address string put in because it might not have to netloc or scheme, which is http or ftp, those things

    e.g. of USAGE EY : 20140718
    skngalpha_url = "seekingalpha.com"
    sknga_parts = urlparts( sknalpha_url )  
    sknga_parts.urlout()
    """

    # cf. https://agiliq.com/blog/2012/06/understanding-args-and-kwargs/  # this explains very well the ordering
    def __init__(self, url, *args, **kwargs):
        SCHEME = "http"

        try:
            self._prsd = urlparse(url)
            self._prsdd = dict( zip( self._prsd._fields , [ value for value in self._prsd ] ) )
            for key in self._prsdd:
                setattr(self, key , self._prsdd[key])

        except (AttributeError, TypeError) as e_err:
            print e_err
            print "string wasn't given"

            # at least populate the parameters needed for urlunparse
            for key in urlparse('')._fields:
                setattr(self,key,'')
            
            for dictionary in args:
                for key in dictionary:
                    if key in urlparse('')._fields:
                        setattr(self, key, dictionary[key])

            for key in kwargs:
                if key in urlparse('')._fields:
                    setattr(self, key, kwargs[key] )
            # cf. http://stackoverflow.com/questions/2466191/set-attributes-from-dictionary-in-python This is a great answer from Ian Clelland

        #
        # the scheme fixing test, the following code is for fixing the scheme of the url         
        #
        if self.scheme == '':
            self.scheme = SCHEME # default scheme, need it

        if not self.netloc:
            self.netloc, self.path = self.path, ''  # cf. http://stackoverflow.com/questions/3798269/combining-a-url-with-urlunparse

        if self.query and not self.query == '':
            self.qs = dict( parse_qsl(self.query) )
                
    def mkquery(self):
        """
        mkquery - make the query from the dictionary in the attribute qs
        """
        self.query = urlencode(self.qs)

    def splitpath( self ):
        if self.path == '':
            return ''
        
        else:
            self.BASEPATH = basename( self.path )
            self.DIRPATH  = dirname( self.path)
            return ( self.BASEPATH , self.DIRPATH )

    def Urljoin(self, url2 ):
        return urljoin( self.urlout() , url2 )
        
    def urlout(self):
        return urlunparse((self.scheme, self.netloc, self.path, self.params, self.query , self.fragment))

    def NetLocOut(self):
        return urlunparse((self.scheme, self.netloc, '', '', '', '' ) )

    def __repr__(self):
        return str(self.urlout())
