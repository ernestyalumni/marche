# marche
marche - Web scraping, Data Wrangling, databasing (with SQLAlchemy and PostgreSQL) of securities for financial markets

This is copied off of tempdoc.doc, but with (slightly) better formatting:

##Quick Start: ##
###Build: ###

- Go edit *firms_by_NASDAQ.py* and replace the string “iamauser” with the username you want to use for your SQL database.
- Be sure to configure the SQLAlchemy engine with your choice of SQL database in *firms_by_NASDAQ.py*

Then run the following in their directories:

```  
  python -i firms_by_NASDAQ.py
  python -i YHOOF_toSQL.py 
  ```

Then, after every trading day, update the table of Historical Prices by running the following:

```  
python -i apres_YHOOFhp.py
```

Then use the following SQL table-mapper classes to make SQLAlchemy session queries:

* security
* Symbole
* YHOOF_HISTP_datapt as YfHP_pt

with 

* security - yields, for each security, firm, stock, or company listed in the NYSE, AMEX, or NASDAQ the IPOyear, Last Sale, Market it belongs to, Market Capitalization, its (long) name, Sector, Symbol, industry it belongs
* Symbole - a SQLalchemy class mapper to table “symbole_table” which is a table of only ticker symbols (it’s fast to query this table if you only want ticker symbols)
* YHOOF_HISTP_datapt as YfHP_pt - all historical prices for all possible securities, firms, stocks, or companies listed in the NYSE, AMEX, or NASDAQ


##Start here with##
###firms_by_NASDAQ.py###

If you’re building the SQL database of all the present firms (i.e. symbols, tickers, stocks) that are listed by the NASDAQ website for NASDAQ, AMEX, and NYSE, then do this:

- Go edit the Python script firms_by_NASDAQ.py and replace the string “iamauser” with the username you want to use for your SQL database.
- Be sure to configure the SQLAlchemy engine with your choice of SQL database.  For instance, I use postgresql, so I used “postgresql://“ in create_engine.  Also, it’s located in a localhost for the postgreSQL database named ‘marche’, i.e. first, I created, with createdb the PostgreSQL database marche.  Then, I have to “call it” with the SQLAlchemy engine.  

```
python firms_by_NASDAQ.py
```

in its directory.  


###apres_firms_by_NASDAQ.py###

The available SQLalchemy classes that map to tables are the following:

* securityNASDAQ
* securityAMEX
* securityNYSE
* security
* Symbole

where

* securityNASDAQ - information on a security (i.e. firm, stock, company) listed solely on NASDAQ
* securityAMEX - information on a security (i.e. firm, stock, company) listed solely on AMEX
* securityNYSE - information on a security (i.e. firm, stock, company) listed solely on NYSE
* security - information on a security (i.e. firm, stock, company) listed in all 3, NASDAQ, AMEX, NYSE, that is sourced from the NASDAQ website
* Symbole - this class maps to a table that only contains unique ticker symbols


###YHOOF_toSQL.py###

Recall that 

  ```
  session.query(Symbole).all()
  ```

gets all the (ticker) symbols, with no duplicates, as a Python list.  

run 

  ```
  python -i YHOOF_toSQL.py
  ```

and answer “yes” at the prompt to build the entire SQL database of historical prices for all available data from Yahoo! Finance for all firms (i.e. stocks, tickers, companies) in the NASDAQ, NYSE, AMEX, according to the NASDAQ website.



