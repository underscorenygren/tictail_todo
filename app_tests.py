import os
import unittest
import json

import server

MONGO_TEST_DB = 'tictailtodo_test'
USR_NAME = 'erik'
USR_ID = 'testusr'

def _url(name):
  return "%s/%s" % (USR_ID, name)

def _todo_url(todo_id, endpoint):
  path = "todo/%s/%s" % (todo_id, endpoint)
  return _url(path)


class AppTestCase(unittest.TestCase):

  def setUp(self):
    app = server.app
    app.connect_to_db(MONGO_TEST_DB)
    app.conn.drop_database(MONGO_TEST_DB)

    self.app = app.test_client()
    self.todo_orm = app.todo_orm

    usr = app.todo_orm.create_user()
    usr.update(USR_NAME, USR_ID)

  def _json(self, route, post_data = None, assert_200 = True):
    if post_data != None:
      resp = self.app.post(route, data=post_data)
    else:
      resp = self.app.get(route)

    if assert_200:
      assert resp.status_code == 200

    obj = json.loads(resp.data)
    return obj

  def test_01_initial(self):
    """this test is run first, 
    tests initial state. 
    
    On second thought, this doesn't appear
    to work"""

    users_at_start = 1
    n_users = self.todo_orm.n_users()
    default_usr = self.todo_orm.ensure_user(USR_ID)

    assert n_users == users_at_start
    assert default_usr == True

  def test_index(self):
    """Creates a user and redirects"""
    n_users = self.todo_orm.n_users()
    resp = self.app.get('/')

    assert resp.status_code == 302
    assert n_users + 1 == self.todo_orm.n_users()

  def test_no_get_create(self):
    """Cannot GET on POST endpoint"""
    
    resp = self.app.get(_url('/todo/create'))
    assert resp.status_code >= 400

  def test_create_delete(self):
    data = self._json(_url('todos'))

    _todos = data.get('todos', None)
    assert _todos != None
    assert len(_todos) == 0

    todo = self._json(_url("todo/create"), 
                  {"text" : u"test"})
    assert todo['text'] == u"test"
    assert todo['done'] == False

    data = self._json(_url('todos'))
    _todos = data.get('todos', None)
    assert _todos != None
    assert len(_todos) == 1

    todo = self._json(_todo_url(todo['id'], 'delete'), {})
    assert todo['text'] == 'test'

    data = self._json(_url('todos'))
    _todos = data.get('todos', None)
    assert _todos != None
    assert len(_todos) == 0

  def test_updates(self):
    todo = self._json(_url("todo/create"), 
                  {"text" : u"new test"})
    assert todo['text'] == u"new test"
    assert todo['done'] == False
    assert todo['priority'] == 1
    todo_id = todo['id']

    self._json(_todo_url(todo_id, 'done'), {})
    todo = self._json(_todo_url(todo_id, 'get'))
    assert todo['done'] == True

    self._json(_todo_url(todo_id, 'done'), {})
    todo = self._json(_todo_url(todo_id, 'get'))
    assert todo['done'] == False

    self._json(_todo_url(todo_id, 'text'), 
      {'text' : u'newnew'})
    todo = self._json(_todo_url(todo_id, 'get'))
    assert todo['text'] == 'newnew'

    self._json(_todo_url(todo_id, 'incprio'), {})
    todo = self._json(_todo_url(todo_id, 'get'))
    assert todo['priority'] == 2
    
    self._json(_todo_url(todo_id, 'decprio'), {})
    todo = self._json(_todo_url(todo_id, 'get'))
    assert todo['priority'] == 1

    #Cannot go lower than 1
    self._json(_todo_url(todo_id, 'decprio'), {})
    todo = self._json(_todo_url(todo_id, 'get'))
    assert todo['priority'] == 1

    self._json(_todo_url(todo_id, 'incprio'), {})
    todo = self._json(_todo_url(todo_id, 'get'))
    assert todo['priority'] == 2

    self._json(_todo_url(todo_id, 'incprio'), {})
    todo = self._json(_todo_url(todo_id, 'get'))
    assert todo['priority'] == 3

    self._json(_todo_url(todo_id, 'incprio'), {})
    todo = self._json(_todo_url(todo_id, 'get'))
    assert todo['priority'] == 4

    self._json(_todo_url(todo_id, 'incprio'), {}) #4 again (max)
    todo = self._json(_todo_url(todo_id, 'get'))
    assert todo['priority'] == 4
 

if __name__ == "__main__":
  
  unittest.main()
