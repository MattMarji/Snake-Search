# This will contain the core functions and algorithms needed for Snake Search
import imp
import sqlite3 as sql
# import crawler from this directory, not from the installed directory.
crawler = imp.load_source('crawler', 'crawler.py')

try:
	db_conn = sql.connect('snake_search.db')
except:
	print ("error connecting to db")

crawl = crawler.crawler(db_conn, 'urls.txt')

crawl.crawl(depth=1)
