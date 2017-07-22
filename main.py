#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
import os

import urllib, urllib2, Cookie

import webapp2

from google.appengine.api import users
from google.appengine.ext.webapp import template

import os
import words


fontList = []

Language = 'Lakota'

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello Lakota world!')


class KeyboardHandler(webapp2.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    if not current_user:
      user_nickname = None
      user_logout = None
      logging.info('*** Not signed in ***')
    else:
      logging.info('*** user nickname = %s, email= %s , admin = %s***, id = %s' %
        (current_user.nickname(), current_user.email(),
        users.is_current_user_admin(), current_user.user_id()))
      user_logout = users.create_logout_url('/')
      user_nickname = current_user.nickname()
     
    fontList = []
    template_values = {
      'user_nickname': user_nickname,
      'user_logout': user_logout,
      'fontFamilies': fontList,
      'language': Language,
    }
    
    path = os.path.join(os.path.dirname(__file__), 'keyboard.html')
    self.response.out.write(template.render(path, template_values))


class WordsHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello Lakota words!')


class DatabaseHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello Lakota database!')


class SetCookieHandler(webapp2.RequestHandler):
  def get(self):
    req = self.request
    url = req.url
    cookies = req.cookies
    template_values = {
      'fontFamilies': fontList,
      'language': Language,
      'cookies': cookies,
      'url': url,
    }
    self.response.headers.add_header(
	  'Set-Cookie', 'email=abc@john.com;expires=31-Dec-2017 23:59:59 GMT') 
    path = os.path.join(os.path.dirname(__file__), 'cookie.html')
    self.response.out.write(template.render(path, template_values))


class TestCookieHandler(webapp2.RequestHandler):
  def get(self):
    req = self.request
    url = req.url
    cookies = Cookie.SimpleCookie() 
    logging.info('url = %s, cookies = %s' % (url, cookies))
    self.response.write('Hello cookie') 


class LoginPageHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    #logging.info(' ***** AUTH_DOMAIN = %s' %os.environ.get('AUTH_DOMAIN'))
    logging.info('UUUUU = %s', user)
    if user:
      nickname = user.nickname()
      logout_url = users.create_logout_url('/')
      greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(
        nickname, logout_url)
      login_url = None
    else:
      nickname = None
      logout_url = None
      login_url = users.create_login_url('/')
      greeting = '<a href="{}">Sign in</a>'.format(login_url)

    logging.info('UUUUU greeting = %s', greeting)

    #self.response.write(
    #  '<html><body>{}</body></html>'.format(greeting))

    template_values = {
      'user_nickname': nickname,
      'user_logout': logout_url,
      'user_login_url': login_url,
      'language': Language,
    }
    path = os.path.join(os.path.dirname(__file__), 'login.html')
    self.response.out.write(template.render(path, template_values))


app = webapp2.WSGIApplication([
    ('/', KeyboardHandler),  # Maybe implement another thing sometime.
    ('/keyboard/', KeyboardHandler),
    ('/login/', LoginPageHandler), 
    ('/words/', words.WordHandler),
    ('/words/addPhrase/', words.AddPhrase),
    ('/words/clear/', words.ClearWords),
    ('/words/getWords/', words.GetWordsHandler),
    ('/words/getPhrases/', words.GetPhrases),
    ('/words/startUpload/', words.SolicitUpload),
    ('/words/updateStatus/', words.UpdateStatus),
    ('/words/upload/', words.ProcessUpload),
    ('/words/uploadCSV/', words.ProcessCSVUpload),
    ('/words/dbName/', words.AddDbName),
    ('/test/trycookie/', SetCookieHandler),
    ('/test/cookie/', TestCookieHandler),
    ('/users/', words.GetUserHandler),
    ('/addUser/', words.AddUserHandler),
], debug=True)
