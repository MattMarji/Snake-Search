#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
if 'threading' in sys.modules:
    del sys.modules['threading']
import gevent
import gevent.socket
import gevent.monkey
gevent.monkey.patch_all()

import re
import json
import httplib2
import urllib
from bottle import *
import bottle.ext.sqlite as sqlite
from collections import OrderedDict
from collections import Counter
from bottle import error
from collections import Counter
from operator import itemgetter
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from beaker.middleware import SessionMiddleware

# Globals persisting information about users

emaildict = OrderedDict()
user_history = OrderedDict()

# Session information

session_opts = {'session.type': 'memory', 'session.auto': True}

# Specifying connection params to db

plugin = sqlite.Plugin(dbfile='./snake_search.db')
_bottleApp = app()
_bottleApp.install(plugin)
app = SessionMiddleware(_bottleApp, session_opts)


# Hook before a request is processed

@hook('before_request')
def update_auth_state():

    # only authenticated users can hit these urls

    restricted_urls = ['/signout']

    # state vars

    s = request.environ.get('beaker.session')

    # views load in either authenticated or unauth content depending on the state of logged_in...

    logged_in = (True if s and 'user_email' in s and s['user_email'
                 ] else False)

    # save path url here

    BaseTemplate.defaults['path'] = request.path

    if logged_in == False and request.path in restricted_urls:
        return redirect('/')
    else:
        BaseTemplate.defaults['user_email'] = (s['user_email'] if s
                and 'user_email' in s and s['user_email'] else False)
        BaseTemplate.defaults['logged_in'] = logged_in
        return


### Routes ###

# 404 route

@error(404)
def error404(error):
    return template('views/error.tpl')


# Establishing home page and static assets

@route('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='./static/')


# Sign out

@route('/signout')
def signout():
    session = request.environ.get('beaker.session')
    session['user_email'] = False
    redirect('/')


# Sign in

@route('/signin')
def signin():

     # Step2: App server generates auth URL base on client ID

    flow = flow_from_clientsecrets('client_secrets.json',
                                   scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'
                                   ,
                                   redirect_uri='http://ec2-52-5-243-14.compute-1.amazonaws.com/redirect'
                                   )
    uri = flow.step1_get_authorize_url()
    redirect(str(uri))


# Redirect to authorize user, extract user email and create session

@route('/redirect')  # query entered in SIGN IN MODE
def redirect_page():
    code = request.query.get('code', '')
    flow = \
        OAuth2WebServerFlow(client_id='1011735639727-i12ach2k55gogrfl603e9fl1ub2u5rm0.apps.googleusercontent.com'
                            , client_secret='GDrQHnGCjVoDLJLgP5p7IyAr',
                            scope='https://www.googleapis.com/auth/calendar'
                            ,
                            redirect_uri='http://ec2-52-5-243-14.compute-1.amazonaws.com/redirect'
                            )
    credentials = flow.step2_exchange(code)
    token = credentials.id_token['sub']
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Get user email

    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']

    # At this point we create a session for the signed-in user.

    session = request.environ.get('beaker.session')  # session is a dictionary

    # saving user_email as key, and value is token

    session[user_email] = token

    # saving user_email as a value here, using as an identifier for authenticated state.

    session['user_email'] = user_email
    redirect('/')


# Establishing Easter-Egg route

@route('/secret')
def secret():
    return static_file('snake_game.html', root='./views/')


# Keyword search in JSON form for autocomplete suggestions
# http://localhost:8080/api/?keywords=andrew

@route('/api/', method='GET')
def api(db):
    try:
        raw_query_string = request.query['keywords'].lower()
        raw_query_string = re.findall('\w+', raw_query_string)
        if len(raw_query_string) < 1:
            return dict(data=[])
    except KeyError:
        return dict(data=[])
    results = list(pageranked_url_fetcher(db, raw_query_string))
    index = ['link', 'description', 'score']
    r = [dict((index[i], value) for (i, value) in enumerate(row))
         for row in results]
    return dict(data=r)


# if keyword argument has one result, navigate to it.
# else redirect to / with the same keywords arguments

@route('/lucky', method='GET')
def lucky(db):
    try:  # check if the user is passing keywords in the URL (request)
        raw_query_string = request.query['keywords']
        raw_query_string = re.findall('\w+', raw_query_string)
        if len(raw_query_string) < 1:
            return redirect('/?keywords=' + request.query['keywords'])
    except KeyError:
        return redirect('/?keywords=' + request.query['keywords'])

    results = list(pageranked_url_fetcher(db, raw_query_string))
    index = ['link', 'description', 'score']
    r = [dict((index[i], value) for (i, value) in enumerate(row))
         for row in results]

    # grab top result URL and send user to it

    if len(r) > 0:
        redirect(r[0]['link'])
    else:
        redirect('/?keywords=' + request.query['keywords'])


# Landing/query page route

@route('/', method='GET')
def main(db):

    # extracting the global variable dictionary beaker.session

    session = request.environ.get('beaker.session')

    try:  # check if the user is passing /?keywords in the URL (request)
        raw_query_string = request.query['keywords']
        raw_query_list = re.findall('\w+', raw_query_string)
    except KeyError:
        return template('views/home.tpl')

    user_email = 'user_email' in session and session['user_email']

    return template(
        'views/results.tpl',
        query_str=raw_query_string.lower(),
        pagerankedList=pageranked_url_fetcher(db, raw_query_list),
        resDict=results(raw_query_list),
        historyDict=history(user_email),
        recentList=recentlysearched(raw_query_list, user_email),
        )


### View Helper Functions ###

# Updates a user's word counts

def record_user_search(user_email, query_str_list):
    if user_email:
        if user_email not in emaildict:
            emaildict[user_email] = Counter()
        for w in query_str_list:
            emaildict[user_email][w] += 1
    else:
        return False


# Returns user's top 20 queried words as an OrderedDict

def history(user_email):
    if user_email:
        historyDict = emaildict[user_email]
        return OrderedDict(Counter(historyDict).most_common(20))
    else:
        return False


# Return Query Word & Count as an OrderedDict

def results(query_str_list):

    # returns the count of words that user has queried (cumulating word count but only to show words of
    # those which user has last queried)

    resDict = Counter()  # declaring ordered dictionary datastructure
    for w in query_str_list:  # for each word in user query
        resDict[w] += 1
    return resDict


# Returns user's 10 most recently searched word as a List

def recentlysearched(query_str_list, user_email):
    if user_email:
        tblstr = ''
        templst = []

        if user_email not in user_history:
            user_history[user_email] = []

        user_history[user_email] = user_history[user_email] \
            + query_str_list
        len_of_rss_array = len(user_history[user_email])

        templst = user_history[user_email][::-1]
        templst = templst[:10]

        return templst
    else:
        return False


# Fetches links and their pagerank scores
# associated with the first word of the user's query

def pageranked_url_fetcher(db, query_str_list):

    # Need to pass arguments in as a tuple or an array.

    unranked = \
        "select doc_index.doc_id, doc_index.doc_url, doc_index.doc_url_title from lexicon,inverted_index,doc_index where lexicon.word_id=inverted_index.word_id and inverted_index.doc_id=doc_index.doc_id and lexicon.word='{0}'"
    unranked_query = ' intersect '.join([unranked.format(arg)
            for arg in query_str_list])
    unranked_query = '(' + unranked_query + ')'
    cursor = \
        db.execute('select distinct doc_url, doc_url_title, doc_rank from {0}unranked left join page_rank on unranked.doc_id=page_rank.doc_id order by page_rank.doc_rank desc;'.format(unranked_query))
    results = cursor.fetchall()
    return results


run(app=app, port=8080, debug=True, server='gevent')
