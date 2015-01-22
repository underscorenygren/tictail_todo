import os
import unittest
import json

import server

MONGO_TEST_DB = 'tictailtodo_test'
USR_NAME = 'erik'
USR_ID = 'testusr'

def _url(name):
  return "%s/%s" % (USR_ID, name)

def _del(todo):
  todo_id = todo['id']
  path = "todo/%s/delete" % todo_id
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

  def _json(self, route, use_post = False, assert_200 = True):
    if use_post:
      resp = self.app.post(route)
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

    todo = self._json(_url("todo/create"), True)
    assert todo['text'] == u"test"
    assert todo['done'] == False

    data = self._json(_url('todos'))
    _todos = data.get('todos', None)
    assert _todos != None
    assert len(_todos) == 1

    todo = self._json(_del(todo), True)
    assert todo['text'] == 'test'

    data = self._json(_url('todos'))
    _todos = data.get('todos', None)
    assert _todos != None
    assert len(_todos) == 0

if __name__ == "__main__":
  
  unittest.main()
