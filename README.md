# Snake Search

Description
===========

This is the official implementation of the Snake Search back-end.
Snake Search is a search engine that will use two Python libraries (Crawler and BeautifulSoup) to traverse a list of known url's for words that match the query sent by a user.

RUN CRAWLER.PY
====================
A simple set of calls to Crawler have been created in snake_searcher.py

It will simply import crawler, run it with the urls.txt file included, and output both the inverted_index and resolved_inverted_index!

TEST CRAWLER.PY
====================
Four tests have been written to test the implementation of crawler.
These tests will test against a STATIC page that I have uploaded to www.matthewmarji.com/test_page.html which is HTML with four words 'This is a test'

To run the tests, simply traverse to the directory and run 'python crawler.py'

LAB 1 IMPLEMENTATION
====================

In Lab 1 we are given a base version of crawler.py. This version does not have a inverted index, nor a resolved inverted index. Also, we currently do NOT save the keywords to a database. All data is cached in memory and is never persisted.

We have added the following variables:

	self._inverted_index = { }
	self._resolved_inverted_index = { }

	## MAPS word_id => word ##
	self._index_words_by_id = { }

	## MAPS doc_id => url (string) ##
	self._index_urls_by_id = { }

	## FOR FUTURE USE: stores the title for a certain doc_id ##
	self._doc_title_cache = { }

	## FOR FUTURE USE: stores the description for a certain doc_id ##
	self._doc_desc_cache = { }

We have added two new functions:

	## Returns the current inverted index ##
	def get_inverted_index(self):

	## Returns the resolved inverted index ##
	def get_resolved_inverted_index(self):


