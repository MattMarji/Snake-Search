
# Copyright (C) 2011 by Peter Goodman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import unittest
import urllib2
import urlparse
from BeautifulSoup import *
from collections import defaultdict
import re
import redis
import sqlite3 as lite
from pagerank import page_rank

def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):

        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }
        self._links_cache = [ ]
        self._title_cache = [ ]
        self._inverted_index = { }
        self._resolved_inverted_index = { }
        self._index_words_by_id = { }
        self._index_urls_by_id = { }
        self._url_title_cache = { }
        self._doc_title_cache = { }
        self._doc_desc_cache = { }

        # Initialize DB (SQLite)    
        self._db_conn = db_conn
        self._db_cursor = db_conn.cursor()
        self.initialize_databases()

        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title an increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame',
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset',
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass

    def initialize_databases(self):
        self._db_cursor.execute('CREATE TABLE IF NOT EXISTS lexicon(word_id INTEGER PRIMARY KEY, word TEXT NOT NULL UNIQUE);')

        self._db_cursor.execute('CREATE TABLE IF NOT EXISTS page_rank(doc_id INTEGER NOT NULL UNIQUE, doc_rank FLOAT);')

        self._db_cursor.execute('CREATE TABLE IF NOT EXISTS inverted_index (word_id INTEGER NOT NULL, doc_id INTEGER NOT NULL, PRIMARY KEY (word_id, doc_id));')

        self._db_cursor.execute('CREATE TABLE IF NOT EXISTS doc_index(doc_id INTEGER PRIMARY KEY, doc_url TEXT UNIQUE, doc_url_title TEXT);')


    def insert_word(self, word):
        """Insert a word into the lexicon. and return the word ID of the inserted word."""

        # Insert word...
        self._db_cursor.execute('INSERT OR IGNORE INTO lexicon(word) VALUES("%s");' % word)

        # Get word_id...
        self._db_cursor.execute('SELECT word_id FROM lexicon WHERE word = "%s"' % word)

        word_id = self._db_cursor.fetchone()[0]
        assert(word_id > 0)

        return word_id


    def insert_into_inverted_index(self):
        """Insert a word_id and it's set of doc_ids into the db store of the inverted index."""

        for word_id, doc_ids in self._inverted_index.iteritems():
                #print 'word_id = ', word_id, '| doc_ids = ', doc_ids
                for doc_id in doc_ids:
                    self._db_cursor.execute('INSERT OR IGNORE INTO inverted_index(word_id, doc_id) VALUES (%d, %d);' % (word_id, doc_id))


    def insert_pagerank(self):
        """Insert the page ranking of the specific page accessed"""

        if len(self._links_cache) > 0:
            link_rankings = page_rank(self._links_cache)

            for doc_id, doc_rank in link_rankings.iteritems():
                self._db_cursor.execute('INSERT OR IGNORE INTO page_rank(doc_id, doc_rank) VALUES (%d, %f);' % (doc_id, doc_rank))

    def insert_document(self, url):
        """Insert url into doc_index DB and return the url doc_id."""

        doc_url_title = ''

        if url in self._url_title_cache:
            doc_url_title = self._url_title_cache[url]

        # Insert the URL and the matching URL title into the doc_index DB.
        self._db_cursor.execute('INSERT OR IGNORE INTO doc_index(doc_url, doc_url_title) VALUES ("%s", "%s");' % (url, doc_url_title))

        # Retrieve the matching doc_id for the inserted URL.
        self._db_cursor.execute('SELECT doc_id FROM doc_index WHERE doc_url = "%s"' % url)

        doc_id = self._db_cursor.fetchone()[0]
        assert(doc_id > 0)

        return doc_id


    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]

        word_id = self.insert_word(word)
        self._word_id_cache[word] = word_id
        return word_id

    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]

        doc_id = self.insert_document(url)
        self._doc_id_cache[url] = doc_id
        self._index_urls_by_id[doc_id] = url
        return doc_id

    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""

        # compute the new url based on import
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        self._links_cache.append((from_doc_id, to_doc_id))

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        print "document title="+ repr(title_text)
        self._doc_title_cache[self._curr_doc_id] = title_text

        # TODO update document title for document id self._curr_doc_id

    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        # Save the key-value pair (destination-url -> URL title)
        self._url_title_cache[dest_url] = self._text_of(elem).strip()

        print "href="+repr(dest_url), \
              "title="+repr(self._text_of(elem).strip()), \
              "alt="+repr(attr(elem,"alt")), \
              "text="+repr(self._text_of(elem).strip())

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))

        # add a link entry into the database from the current document to the
        # other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))


    def _add_words_to_document(self):
        # Go through each word, add it to the inverted index.
            # IF the word exists already, append the doc_id to the set
            # ELSE add the word_id as the key, and create a set with the doc_id as the first element..
        for word_id, font_size in self._curr_words:
            if word_id in self._inverted_index:
                # a matching word exists. Add to the existing set.
                self._inverted_index[word_id].add(self._curr_doc_id)
            else:
                # word does not exist, add key-value pair of word_id -> set(doc_id)
                self._inverted_index[word_id] = set([self._curr_doc_id])

    def get_inverted_index(self):
        return self._inverted_index

    def get_resolved_inverted_index(self):
        # take the inverted index (word_id: set([doc_id, doc_id...]))
        # substitute the word_id with the word (string) and the doc_id with the url (string)

        for word_id in self._inverted_index:

            # Get the word string
            word = self._index_words_by_id[word_id]
            self._resolved_inverted_index[word] = set([])

            # Traverse set and get each word.
            for doc_id in self._inverted_index[word_id]:
                url = self._index_urls_by_id[doc_id]
                self._resolved_inverted_index[word].add(url)

        return self._resolved_inverted_index

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it

    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""

        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue

            self._curr_words.append((self.word_id(word), self._font_size))
            self._index_words_by_id[self.word_id(word)] = word

    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))

            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''

        class NextTag(object):
            def __init__(self, obj):
                self.next = obj

        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)

                    continue

                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id) # mark this document as haven't been visited

            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                print "    url="+repr(self._curr_url)

            except Exception as e:
                print e
                pass
            finally:
                if socket:
                    socket.close()

        # Crawling is complete - start saving to the database!

        # Insert and update the page ranking system.
        self.insert_pagerank()

        # Insert and update the inverted_index DB.
        self.insert_into_inverted_index()

        # Save all DB changes!
        self._db_conn.commit()

        # Close DB connection on completion of crawling.
        self._db_conn.close()


class TestCrawlerMethods(unittest.TestCase):
    def setUp(self):
        self.crawl = crawler(None, 'test_urls.txt')
        self.crawl.crawl(depth=1)
        self.inverted_index = self.crawl.get_inverted_index()
        self.resolved_inverted_index = self.crawl.get_resolved_inverted_index()

    def test_for_incorrect_keywords(self):
        # Ensure no other words were parsed such as filler words (is,a, etc...)
        with self.assertRaises(KeyError):
            self.resolved_inverted_index['is'] != None
            self.resolved_inverted_index['a'] != None

    def test_for_correct_keywords(self):
        # Test for expected keywords 'this' and 'test'
        assert ('this' in self.resolved_inverted_index)
        assert ('test' in self.resolved_inverted_index)

    def test_for_correct_url(self):
        # We expect the url to be the one specified in the test_urls.txt file
        assert (self.resolved_inverted_index['this'] == set(['http://matthewmarji.com/test_page.html']))
        assert (self.resolved_inverted_index['test'] == set(['http://matthewmarji.com/test_page.html']))

    def test_for_no_repition(self):
        # Ensure that although we have 2 words, we have 1 URL (no repeat)
        assert (len(self.crawl._doc_id_cache) == 1)

if __name__ == "__main__":
    unittest.main()
