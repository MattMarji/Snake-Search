# This will contain the core functions and algorithms needed for Snake Search
from crawler import crawler
crawl = crawler.crawler(None, 'urls.txt')
crawl.crawl(depth=1)
print crawl.get_inverted_index()
print crawl.get_resolved_inverted_index()

'''
word_match = {}
words = {}
urls = {}
documents = {}

def add_keyword(keyword):
    word_match[keyword] = len(word_match) + 1
    return word_match[keyword]

def add_url(url):
    urls[url] = len(urls) + 1

# This function will take in the keyword and the doc ID
def add_doc_id

def get_inverted_index():
    return words

def get_resolved_inverted_index():
    # We will construct a mapping of the ids to the key values (strings) and return that dictionary.

    resolved_index = {}
    for word in words:
        resolved_index[resolve_keyword_index()]



# This function will take a keyword index as the parameter and return the keyword string.
def resolve_keyword_index():
    print "Not yet ready to do that..."

# This function will take the document index as the parameter and return the URL set of strings.
def resolve_doc_index():
    print "Not yet ready to do that..."

add_keyword('google')
add_keyword('search')
add_keyword('terms')

add_url("https://google.ca")
add_url("https://google.com")

words[word_match['google']] = (1,2,5)
words[word_match['search']] = (1,3,4)
words[word_match['terms']]  = (2,3,4,5)

documents[1] = (urls["https://google.ca"], urls["https://google.com"])
documents[2] = (urls["https://google.ca"])
documents[3] = (urls["https://google.ca"], urls["https://google.com"])
documents[4] = (urls["https://google.ca"], urls["https://google.com"])
documents[5] = (urls["https://google.ca"])
'''
