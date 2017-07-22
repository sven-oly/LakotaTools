# -*- coding: utf-8 -*-
#!/usr/bin/env python

import main

import csv
import json
import logging
import os
import StringIO

import urllib
import webapp2

# Help from http://nealbuerger.com/2013/12/google-app-engine-import-csv-to-datastore/
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import db

from google.appengine.api import users
from google.appengine.ext.webapp import template

# dbName will allow multiple sets of information to be stored and retrieved by that
# value. Added 14-Mar-2017

class PhraseDB(db.Model):
  index = db.IntegerProperty()
  dbName = db.StringProperty(u'')
  lastUpdate = db.DateTimeProperty(auto_now=True, auto_now_add=True)
  englishPhrase = db.StringProperty(multiline=True)
  PhraseLatin = db.StringProperty(u'')
  PhraseUnicode = db.StringProperty(u'')
  status = db.StringProperty('')
  comment = db.StringProperty('')


# The set of registered db names.
class DbName(db.Model):
  dbName = db.StringProperty(u'')
  lastUpdate = db.DateTimeProperty(auto_now=True, auto_now_add=True)


# The set of registered db names.
class UserDatabase(db.Model):
  userEmail = db.StringProperty(u'')
  userPassword = db.StringProperty(u'')
  userPrivileges = db.StringListProperty([])
  updater = db.StringProperty(u'')  # EMail of person adding/updating.
  lastUpdate = db.DateTimeProperty(verbose_name='Last Update', auto_now=True, auto_now_add=True)


# Retrieves data at a given index via AJAX. 
class GetWordsHandler(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    self.response.headers['Content-Type'] = 'text/plain'   

    logging.info('!!!!!!!!!! PUT USER = %s' % (user))
    self.response.out.write('GetWordsHandler received.\n')

  def get(self):
    # Testing authentication
    # https://cloud.google.com/appengine/docs/standard/python/users/
    user = users.get_current_user()
    current_user = users.get_current_user()
    if not current_user:
      logging.info('*** Not signed in ***')
      user_nickname = None
      user_logout = None
      user_login = users.create_login_url('/words/getWords/')
      # TODO: Redirect to login page.
      greeting = '<a href="{}">Sign in</a>'.format(user_login)
      #self.response.write(
      #      '<html><body>{}</body></html>'.format(greeting))
    else:
      logging.info('*** user nickname = %s, email= %s , admin = %s***, id = %s' %
        (current_user.nickname(), current_user.email(),
        users.is_current_user_admin(), current_user.user_id()))
      user_logout = users.create_logout_url('/words/getWords/')
      user_login = ''
      user_nickname = current_user.nickname()
          
    index = int(self.request.get('index', '1'))
    filterStatus = self.request.get('filterStatus', 'All')
    direction = int(self.request.get('direction', '0'))
    dbName = self.request.get('dbName', '')
    
    #logging.info('GetWordsHandler index = %d, filterStatus=>%s<, direction = %d' %
    #   (index, filterStatus, direction))

    q = PhraseDB.all()
    if filterStatus == 'All' or filterStatus == 'all':
      # Get the specified index, with no status filter.
      #logging.info('Going for index = %d' % index)
      q.filter("index =", index)
    else:
      # Set up to get next phrase with required status and index >= query index.
      #logging.info('FILTERING WITH status = %s, index >= %d' % (filterStatus, index))
      q.filter('status =', filterStatus)
      if direction < 0:
        q.filter('index <=', index)
        q.order('-index')
      else:
        q.filter('index >=', index)
        q.order('index')

    result = q.get()  # Use get_multi for more than one?

    #logging.info('RESULT = %s' % (result))
    if result:
      index = result.index
      dbName = result.dbName
      oldtext = result.PhraseLatin
      utext = result.PhraseUnicode
      english = result.englishPhrase
      status = result.status
      comment = result.comment
      errorMsg = '' 
    else:
      oldtext = utext = english = status = ''
      errorMsg = 'No results found'
      comment = ''
    obj = {
        'index': index,
        'dbName': dbName,
        'oldtext': oldtext,
        'utext': utext,
        'english': english,
        'status': status,
        'error': errorMsg,
        'comment': comment,
        'user_nickname': user_nickname,
        'user_logout': user_logout,
    }
    self.response.out.write(json.dumps(obj))

# Show data from word list converted for human verification
class WordHandler(webapp2.RequestHandler):
    def get(self):
      current_user = users.get_current_user()
      if not current_user:
        user_nickname = None
        user_logout = None
        logging.info('*** Not signed in ***')
        # TODO: Redirect to login page.
        user_login = users.create_login_url('/words/')
        greeting = '<a href="{}">Sign in</a>'.format(user_login)
        self.response.write(
            '<html><body>{}</body></html>'.format(greeting))
        allowUpdate = False
        allowAddToDB = False       
      else:
        logging.info('*** user nickname = %s, email= %s , admin = %s***, id = %s' %
          (current_user.nickname(), current_user.email(),
          users.is_current_user_admin(), current_user.user_id()))
        user_login = None
        user_logout = users.create_logout_url('/words/')
        user_nickname = current_user.nickname()
        greeting = 'Welcome, %s' % user_nickname
        # TODO: Get permissions from User DB.
        allowUpdate = True
        allowAddToDB = True       
     
      fontList = []
      index = 1
      oldtext = self.request.get('oldtext', '')
      dbName = self.request.get('dbName', '')
      utext = self.request.get('utext', '')
      english = self.request.get('english', '')
      index = int(self.request.get('index', '1'))
      comment = self.request.get('comment', '')
      status = ''

      q = PhraseDB.all()
      currentEntries = 0
      for p in q.run():
        currentEntries += 1
      q.filter("index =", index)
      result = q.get()

      dbq = DbName.all()
      dbNameList = [p.dbName for p in dbq.run()]

      if result:
        oldtext = result.PhraseLatin
        dbName = result.dbName
        utext = result.PhraseUnicode
        english = result.englishPhrase
        status = result.status
        comment = result.comment
      #logging.info('q = %s' % result)
      template_values = {
        'index': index,
        'dbName': dbName,
        'dbNameList': dbNameList,
        'numEntries': currentEntries,
        'oldtext': oldtext,
        'utext': utext,
        'english': english,
        'comment': comment,
        'status': status,
        'fontFamilies': main.fontList,
        'language': main.Language,
        'user_nickname': user_nickname,
        'user_logout': user_logout,
        'allowUpdate': allowUpdate,
        'allowAddToDB': allowAddToDB,
        'greeting': greeting,
      }
      logging.info('WORDS = %s' % template_values)
      path = os.path.join(os.path.dirname(__file__), 'words.html')
      self.response.out.write(template.render(path, template_values))


# DONE: Add approve
# Add controls for loading records
#     for saving new status
#     for getting records approved or not
#     for showing all records.

class GetDataHandler(webapp2.RequestHandler):
  def get(self):
    # Get info from client on which item.

    self.response.headers['Content-Type'] = 'application/json'   
    
    # TODO: fetch data
    # TODO: put data into return object  
    obj = {

    }
    self.response.out.write(json.dumps(obj))

# Show simple interface for CSV upload.
class SolicitUpload(webapp2.RequestHandler):
  def get(self):
    # upload_url = blobstore.create_upload_url('upload')
    upload_url = '/words/uploadCSV/'

    #logging.info('$$$$$$$$$ upload_url %s' % upload_url)
    q = DbName.all()
    dbNameList = [p.dbName for p in q.run()]
    logging.info('dbNameList = %s' % dbNameList)

    template_values = {
      'upload_url':upload_url,
      'dbNames': dbNameList,
      'language': main.Language,
    }
    path = os.path.join(os.path.dirname(__file__), 'wordsUpload.html')
    self.response.out.write(template.render(path, template_values))

# Add entries in the uploaded CSV to the data store.
# TODO: check for duplicates.
class ProcessUpload(webapp2.RequestHandler): 
  def post(self):
    fileInfo = self.request.get('file')
    self.response.out.write(fileInfo)

    logging.info('$$$$$$$$$ fileInfo = %s' % fileInfo)

    # Update with new data.
    # TODO: check for duplicates
    q = PhraseDB.all()
    numEntries = 0
    for p in q.run():
      numEntries += 1
    #logging.info('### Starting at index %d' % numEntries)
    self.response.out.write('### Starting at index %d' % numEntries) 
    startIndex = numEntries + 1
    currentIndex = startIndex
    stringReader = unicode_csv_reader(StringIO.StringIO(fileInfo))
    for row in stringReader:
      entry = processRow(currentIndex, row)
      currentIndex += 1
      numEntries += 1
      self.response.out.write(entry) 

    #logging.info('### StartIndex = %d. %d new entries added' % (startIndex, numEntries - startIndex))
    self.response.out.write('### StartIndex = %d. %d new entries added' % (startIndex, numEntries - startIndex)) 
    q = PhraseDB.all()
    currentEntries = 0
    for p in q.run():
      currentEntries += 1
    self.response.out.write('!!! Current entries now = %d.' %
      (currentEntries)) 


# Clear out the entire phrase data store, or part of it (eventually)
class ClearWords(webapp2.RequestHandler): 
  def get(self):
    q = PhraseDB.all()
    dbName = self.request.get('dbName', '')
    numDeleted = 0
    nullCount = 0
    numEntries =0
    for p in q.run():
      numEntries += 1
      if not p.index:
        nullCount += 1
      if not dbName or p.dbName == dbName:
        PhraseDB.delete(p)
        numDeleted += 1

    # TODO: delete them, with message.
    self.response.out.write('!!! Originally %d index entries.' % numEntries)
    self.response.out.write('!!! Deleted %d null index entries.' % nullCount)
    self.response.out.write('!!! Deleted all of the %s %d entries.' % (dbName, numDeleted))


# Updates the status of an entry and sets the Unicode field.
class UpdateStatus(webapp2.RequestHandler): 
  def get(self):
    index = int(self.request.get('index', '1'))
    dbName = self.request.get('dbName', '')
    newStatus = self.request.get('newStatus', 'Unknown')
    unicodePhrase = self.request.get('unicodePhrase', '')
    oldPhrase = self.request.get('oldData', '')
    comment = self.request.get('comment', '')

    logging.info('Update index = %d, old = %s' % (index, oldPhrase))

    q = PhraseDB.all()
    q.filter("index =", index)
    result = q.get()

    result.status = newStatus;
    result.comment = comment
    if oldPhrase:
      result.PhraseLatin = oldPhrase

    if unicodePhrase:
      result.PhraseUnicode = unicodePhrase
    result.put()
    
    # Send update back to client
    obj = {
      'index': index,
      'status' : result.status,  
      'PhraseLatin' :  oldPhrase,
    }
    self.response.out.write(json.dumps(obj))


class AddPhrase(webapp2.RequestHandler): 
  def get(self):
    oldtext = self.request.get('oldtext', '')
    dbName = self.request.get('dbName', '')
    utext = self.request.get('utext', '')    
    engtext = self.request.get('engtext', '')
    comment = self.request.get('comment', '')

    logging.info('AddPhrase utext = %s, engtext = %s' % (utext, engtext))

    # Check if this already exists.
    q = PhraseDB.all()
    q.filter('PhraseUnicode =', utext)
    result = q.get()
    if result:
      # It's a duplicate. Return warning.
      message = 'This message already exists at index %s' % result.index
    else:
      # It's not there so get new index and store.
      q = PhraseDB.all()
      maxIndex = 0
      for p in q.run():
        if p.index > maxIndex:
          maxIndex = p.index
      entry = PhraseDB(index=maxIndex + 1,
        dbName=dbName,
        englishPhrase=engtext,
        PhraseUnicode=utext,
        comment=comment,
        status='Unknown')
      entry.put()
      message = 'New  message added at index %s' % entry.index  

    response = {
      'message': message,
    }    
    self.response.out.write(json.dumps(response))


# Resets items from database.
class GetPhrases(webapp2.RequestHandler): 
  def get(self):
    user = users.get_current_user()
    current_user = users.get_current_user()
    if not current_user:
      logging.info('*** Not signed in ***')
      user_nickname = None
      user_logout = None
      user_login = users.create_login_url('/words/getPhrases/')
      # TODO: Redirect to login page.
      greeting = '<a href="{}">Sign in</a>'.format(user_login)
      #self.response.write(
      #      '<html><body>{}</body></html>'.format(greeting))
    else:
      logging.info('*** user nickname = %s, email= %s , admin = %s***, id = %s' %
        (current_user.nickname(), current_user.email(),
        users.is_current_user_admin(), current_user.user_id()))
      user_logout = users.create_logout_url('/words/getPhrases/')
      user_login = ''
      user_nickname = current_user.nickname()
          
    filterStatus = self.request.get('filterStatus', '')
    dbName = self.request.get('dbName', '')
    q = PhraseDB.all()
    if filterStatus:
      q.filter('status =', filterStatus)
    # TODO: Filter by dbName.
    q.order('index')

    # All available databases.
    dbq = DbName.all()
    dbNameList = [p.dbName for p in dbq.run()]
    logging.info('dbNameList = %s' % dbNameList)

    numEntries = 0
    entries = []
    nullIndexCount = 0
    for p in q.run():
      numEntries += 1
      if not p.index:
        nullIndexCount += 1
      entry = (p.index, p.englishPhrase, p.PhraseLatin, p.PhraseUnicode,
        p.status)
      entries.append(p)
    # TODO: get them, and sent to client
    template_values = {
      'entries': entries,
      'dbNameList': dbNameList,
      'filter': filterStatus,
      'language': main.Language,
      'user_nickname': user_nickname,
      'user_logout': user_logout,
    }

    path = os.path.join(os.path.dirname(__file__), 'phrasesList.html')
    self.response.out.write(template.render(path, template_values))
  
# Uses blob. TODO: make this work.
class OldProcessUpload(webapp2.RequestHandler): 
   def post(self):
     upload_files = self.get_uploads('file')
     #logging.info('$$$$$$$$$ upload_files %s' % upload_files[1])

     blob_info = upload_files[0]
     #logging.info('$$$$$$$$$ blob_info %s' % blob_info)
     
     entries = process_csv(blob_info)
     blobstore.delete(blob_info.key())  # optional: delete file after import
     
     self.response.headers['Content-Type'] = 'application/json'
     self.response.out.write(self.request.get('csv'))
     # filename = 'data/Approved_Words.Language.xlsx - Sheet1.csv'
     #file = open(os.path.join(os.path.dirname(__file__), filename)) 

     self.response.out.write(entries) 

# To handle UTF-8 input.
def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')
        
def processRow(index, row):
  english, Latin = row
  #logging.info('!! index = %d     english= %s' % (index, english))
  # TODO: dbName
  entry = PhraseDB(index=index,
    englishPhrase=english,
    PhraseLatin=Latin,
    PhraseUnicode='',
    status="Unknown")
  entry.put()
  return entry


class ProcessCSVUpload(webapp2.RequestHandler): 
# http://stackoverflow.com/questions/2970599/upload-and-parse-csv-file-with-google-app-engine
  def post(self):

    #self.response.headers['Content-Type'] = 'text/plain'   
    csv_file = self.request.POST.get('csv_file')
    logging.info('ProcessCSVUpload csv_file = %s' % csv_file)
    dbName = self.request.POST.get('dbName', '')
    logging.info('ProcessCSVUpload dbName = %s' % dbName)
    latinColumn = self.request.POST.get('Column', '')
    englishColumn = self.request.POST.get('englishColumn', 'C')
    commentColumn = self.request.POST.get('commentColumn', '')
    unicodeColumn = self.request.POST.get('unicodeColumn', 'B')
    skipLines = int(self.request.POST.get('skipLines', '1'))

    columns = [latinColumn, englishColumn, commentColumn, unicodeColumn]

    #self.response.out.write('File %s to dbName: %s \n' % (csv_file, dbName))
    #self.response.out.write('Columns: L:%s E:%s C:%s U:%s\n' % (latinColumn, englishColumn, commentColumn, unicodeColumn))
    #self.response.out.write('Skip lines = %d\n' % skipLines)
    
    fileReader = csv.reader(csv_file.file)
    lineNum = 0
    numProcessed = 0
    columnMap = {
      'A' : 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5 }
    # TODO: Add Unicode  utext
    utext = ''
    # TODO: find maxIndex from existing entries in dbNam
    maxIndex = 0

    entries = []
    for row in fileReader:
      # row is now a list containing all the column data in that row
      if lineNum < skipLines:
        x = 1
        #self.response.out.write('Skipping line %d :  %s\n' % (lineNum, row))
      else:
        x = 0
        #self.response.out.write('%3d: %s \n' % (lineNum, row))
        
        try:
          englishPhrase = row[columnMap[englishColumn]]
        except:
          englishPhrase = ''
        try:
          PhraseLatin = row[columnMap[latinColumn]]
        except:
          PhraseLatin = ''
        try:
          comment = row[columnMap[commentColumn]]
        except:
          comment = ''
        try:
          utext = row[columnMap[unicodeColumn]]
        except:
          utext = ''

        try:
          entry = PhraseDB(
            index=maxIndex + 1,
            dbName = dbName,
            englishPhrase = englishPhrase,
            PhraseLatin = PhraseLatin,
            PhraseUnicode = utext,
            comment = comment,
            status = 'Unknown')
          entry.put()
          entries.append(entry)         
          numProcessed += 1
          maxIndex += 1
        except:
          y = 1
          #self.response.out.write('  Cannot set item %d: %s' % (lineNum, row))

      lineNum += 1

    # self.response.out.write('\n %d lines processed\n' % (numProcessed))

    template_values = {
      'dbname': dbName,
      'skipLines': skipLines,
      'columns': columns,
      'numberLoaded': numProcessed,
      'entries': entries,
      'language': main.Language,      
    }
    path = os.path.join(os.path.dirname(__file__), 'DBUploadResults.html')
    self.response.out.write(template.render(path, template_values))

class AddDbName(webapp2.RequestHandler):
  def get(self):
    newName = self.request.get('dbName', '')
    clear = self.request.get('clear', '')

    q = DbName.all()
    if clear:
      # Wipe out DB
      for p in q.run():
        DbName.delete(p)
      return
      
    if not newName:
      nameList = []
      for p in q.run():
        nameList.append(p.dbName)
      self.response.out.write('db Names = %s.\n' % nameList)
      return

    q.filter("dbName =", newName)
    result = q.get()
    
    if result:
      self.response.out.write('db Name = %s is already defined.\n' % newName)
    else:
      entry = DbName(dbName=newName);
      entry.put()
      self.response.out.write('db Name = %s has been added defined.\n' % newName)


class GetUserHandler(webapp2.RequestHandler):

  def get(self):
    # Testing authentication
    # https://cloud.google.com/appengine/docs/standard/python/users/
    user = users.get_current_user()
    current_user = users.get_current_user()
    if not current_user:
      logging.info('*** Not signed in ***')
      user_nickname = None
      user_logout = None
      user_login = users.create_login_url('/words/getWords/')
      # TODO: Redirect to login page.
      greeting = '<a href="{}">Sign in</a>'.format(user_login)
      #self.response.write(
      #      '<html><body>{}</body></html>'.format(greeting))
    else:
      logging.info('*** user nickname = %s, email= %s , admin = %s***, id = %s' %
        (current_user.nickname(), current_user.email(),
        users.is_current_user_admin(), current_user.user_id()))
      user_logout = users.create_logout_url('/words/getWords/')
      user_login = ''
      user_nickname = current_user.nickname()        

    q = UserDatabase.all()

    template_values = {
      'userlist': q,
      'language': main.Language,   
    }
    logging.info('Users = %s' % template_values)
    path = os.path.join(os.path.dirname(__file__), 'users.html')
    self.response.out.write(template.render(path, template_values))


class AddUserHandler(webapp2.RequestHandler):

  def post(self):
    userEmail = self.request.get('userEmail', '')
    userPassword = self.request.get('userPassword', '')  
    userPrivileges = self.request.get('userPrivileges', [])
    updater = self.request.get('updater', '')

    # TODO: Check if this in already in the database.    
    if userEmail:
      entry = UserDatabase(
        userEmail=userEmail,
        userPassword=userEmail,
        userPrivileges=userPrivileges,
        updater=updater
      ) 
      entry.put()
      self.response.out.write('userEmail %s added.\n' % userEmail)
    else:
      self.response.out.write('Empty user email. Nothing added.\n')

    
       
    