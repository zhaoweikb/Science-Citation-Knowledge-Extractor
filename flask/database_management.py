import sqlite3
import time
import datetime
import random

#Basic SQLITE3 structure
#Database in webdev-biotool for managing pmids and scraped webpages
conn = sqlite3.connect(database='pmids_info.db') #connect to database
c = conn.cursor() #cursor


#Define connection and cursor
def connection():
	conn = sqlite3.connect(database='pmids_info.db') #connect to database
	c = conn.cursor() #cursor
	return conn, c


#Input: pmid
#Output: apa citation of that pmid
def db_inputPapers_retrieval(user_input):
	c.execute('''SELECT title, author, journal, pubdate, url FROM inputPapers WHERE pmid=?''', (user_input,))
	for row in c:
		title = row[0]
		author = row[1]
		journal = row[2]
		pubdate = row[3]
		url = row[4]
		apa = str(author+' ('+pubdate+'). '+title+'. '+journal+'. Retrieved from '+url)
		return apa


#Input: pmid
#Output: list of apa citations of pmc-ids citing that pmid
def db_citations_retrieval(user_input):
	c.execute('''SELECT title, author, journal, pubdate, url FROM citations WHERE citesPmid=?''', (user_input,))
	apa_citations = []
	db_journals = []
	db_dates = []
	db_urls = []
	for row in c:
		title = row[0]
		author = row[1]

		journal = row[2]
		db_journals.append(journal)

		pubdate = row[3]
		db_dates.append(pubdate)

		url = row[4]
		db_urls.append(url)

		apa = str(author+' ('+pubdate+'). '+title+'. '+journal+'. Retrieved from '+url)
		apa_citations.append(apa)
	return apa_citations, db_journals, db_dates, db_urls


#Input: pmid that is cited
#Output: list of titles for citation_venn.py
def db_citation_titles(user_input):
	c.execute('''SELECT title, author, journal, pubdate, url FROM citations WHERE citesPmid=?''', (user_input,))
	db_titles = []
	for row in c:
		title = row[0]
		db_titles.append(title)
	return db_titles



#Create table for inputPapers
def create_table_input():
	c.execute('''CREATE TABLE IF NOT EXISTS inputPapers
		(post_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		datestamp TEXT,
		pmid TEXT,
		title TEXT,
		author TEXT,
		journal TEXT,
		pubdate TEXT,
		url TEXT,
		num_citations NUMBER)''')


#Create table for citations of the citations
def create_table_citations():
	c.execute('''CREATE TABLE IF NOT EXISTS citations
		(post_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		datestamp TEXT,
		pmcid TEXT,
		title TEXT,
		author TEXT,
		journal TEXT,
		pubdate TEXT,
		citesPmid TEXT,
		url TEXT,
		abstract TEXT,
		whole_article TEXT,
		sents NUMBER,
		tokens NUMBER)''')


#test
def test_data_entry():
	c.execute("INSERT INTO citations VALUES(0, '09-21-2016', '000', 'title','author', 'journal', 'pubdate', 'pmid', 'www.website.com')")
	conn.commit() #to save it to db
	
	c.execute("SELECT * FROM citations")
	[print(row) for row in c.fetchall()]
	
	c.close()
	conn.close()


#print table
def print_inputPapers():
	c.execute("SELECT * FROM inputPapers")
	[print(row) for row in c.fetchall()]
