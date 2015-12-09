# Snake Search

Description
===========

This is the official implementation of Snake Search.

Snake Search is a search engine that will use two Python libraries (Crawler and BeautifulSoup) to traverse a list of known url's for words that match the query sent by a user.

The stored values will go into multiple SQLite DBs.
The front-end portion of Snake Search uses the bottle framework, but implements Gevent for Asynchronous ability to server a great number of concurrent requests. The front-end connects to the SQLite DB, and queries the tables for the necessary information.

The HTML was built using the Bootstrap framework.

A Load balancer stands in front of two instances of Snake Search to improve concurrency and performance.

DEPLOY SNAKE SEARCH
====================
A deploy script has been created to setup *a single instance* of snake search. The load balancer setup is not automated.

Simply run the deploy.py script. That's it!

RUN CRAWLER.PY
====================
A simple set of calls to Crawler have been created in snake_searcher.py

It will simply import crawler, run it with the urls.txt file included, and output both the inverted_index and resolved_inverted_index!

TEST CRAWLER.PY
====================
Four tests have been written to test the implementation of crawler.
These tests will test against a STATIC page that I have uploaded to www.matthewmarji.com/test_page.html which is HTML with four words 'This is a test'

To run the tests, simply traverse to the directory and run 'python crawler.py'

PART 1 + 2 IMPLEMENTATION
====================

I have added the following variables:

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

	## Returns the current inverted index ##
	def get_inverted_index(self):

	## Returns the resolved inverted index ##
	def get_resolved_inverted_index(self):

PART 3 IMPLEMENTATION
=====================

I introduce a way of saving data to a SQLite database. Easily said, we have the following tables:

	## LEXICON word_id -> word ##
	lexicon(word_id INTEGER PRIMARY KEY, word TEXT NOT NULL UNIQUE)

	## PAGE RANK doc_id -> doc_rank ##
	page_rank(doc_id INTEGER NOT NULL UNIQUE, doc_rank FLOAT)

	## INVERTED_INDEX word_id -> doc_id ##
	inverted_index (word_id INTEGER NOT NULL, doc_id INTEGER NOT NULL, PRIMARY KEY (word_id, doc_id))

	## DOC_INDEX doc_id -> doc_url ##
	doc_index(doc_id INTEGER PRIMARY KEY, doc_url TEXT UNIQUE, doc_url_title TEXT)

PART 4 IMPLEMENTATION
====================

In part 4, we introduce optimizations to our AWS setup. Please refer to our writeup as to how we have optimized our infastructure.

A Load Balancer now sits in front of two instances.

The load balancer can be accessed here: snake-search-lb-1706060925.us-east-1.elb.amazonaws.com

The frontend will connect to the database which has been prepopulated with the urls that have been crawled in the urls.txt file.

BENCHMARKING
====================

Public IP Address:
    52.5.243.14 - Snake Search Instance 1 (ec2-52-5-243-14.compute-1.amazonaws.com)
    52.91.171.44 - Snake Search Instance 2 (ec2-52-91-171-44.compute-1.amazonaws.com)
    snake-search-lb-1706060925.us-east-1.elb.amazonaws.com - Load Balancer

Enabled Google APIs:


Benchmark Setup:

    WRK and ApacheBench was used to test the EC2 instance.
    The machine tested from was a Mac OSX 10.10 with WRK installed.
    The second machine used was a Windows 8 PC with ApacheBench installed via XAMPP.

    The following was run at 3 times during the day. (10AM, 1PM, 6PM)

    wrk -t1 -c3000 -d30s http://52.5.243.14/?keywords=engineering

    The test machine is located in Toronto, Ontario
    The unix instance is located in Virginia, USA

    The Unix machine was running dstat, and running the snake search python script on http://0.0.0.0:80 that replied to requests from WRK. The script can be run as normal

Testing Concurrency:

   We tested concurrency by running ApacheBench on a Windows machine. The following line was run, until we found
   a concurrency value that caused connections to fail.

   ab.exe -n 8000 -c 8000 http://snake-search-lb-1706060925.us-east-1.elb.amazonaws.com/?keywords=engineering

   We continued to increase this value until we reached max concurrency at ~10 000 connections!
   
   Note: we are using Amazon t1.micro instances...pretty impressive, I know. :)


