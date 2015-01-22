import os
import unittest
import json

import server


class AppTestCase(unittest.TestCase):

  def setUp(self):
    self.app = server.app.test_client()
    pass

  def tearDown(self):
    pass


  def _json(self, route, use_post = False, assert_200 = True):
    if use_post:
      resp = self.app.post(route)
    else:
      resp = self.app.get(route)

    if assert_200:
      assert resp.status_code == 200

    obj = json.loads(resp.data)
    return obj

  def test_index(self):
    resp = self.app.get('/')

    assert resp.status_code == 200
    assert resp.content_length > 0

  def test_no_get_create(self):
    
    resp = self.app.get('/create')
    assert resp.status_code >= 400

  def test_create(self):
    posts = self._json('/todos')

    _todos = posts.get('todos', None)
    assert _todos != None
    assert len(_todos) == 0

    todo = self._json("/create", True)
    assert todo['text'] == 'test'
    assert todo['done'] == False


if __name__ == "__main__":
  
  unittest.main()
