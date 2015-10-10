# This will contain the core functions and algorithms needed for Snake Search
import imp
# import crawler from this directory, not from the installed directory.
crawler = imp.load_source('crawler', 'crawler.py')

crawl = crawler.crawler(None, 'urls.txt')
crawl.crawl(depth=1)
print crawl.get_inverted_index()
print crawl.get_resolved_inverted_index()
