# This will contain the core functions and algorithms needed for Snake Search
import imp
import sqlite3 as sql
# import crawler from this directory, not from the installed directory.
crawler = imp.load_source('crawler', 'crawler.py')

db_conn = sql.connect("snake_search.db")

crawl = crawler.crawler(db_conn, 'urls.txt')

crawl.crawl(depth=1)

print crawl.get_inverted_index()
print crawl.get_resolved_inverted_index()
