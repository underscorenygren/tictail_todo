from mongokit import Document
from enum import Enum
import shortuuid
import datetime

class TodoORM():
  
  def __init__(self, mongokit_conn, mongokit_db):
    mongokit_conn.register([MongoTodo, User])
    self.users = mongokit_db.users
    self.todos = mongokit_db.todos

  def create_user(self, name = None, identifier = None):
    usr = self.users.User()
    usr.initialize()

    return usr

  def ensure_user(self, user_id):
    usr = self.users.find({"identifier" : user_id})

    return True if usr else False

  def n_users(self):
    return self.users.count() #Is this optimal way in mongokit?

  def _query_to_json_dict(self, cursor):
    return [MongoTodo.mongo_to_json_dict(todo) for todo in cursor]

  def all_by_user(self, user_id):
    """finds all posts by a user"""
    if not self.ensure_user(user_id):
      return None
    
    _todos = self.todos
      .find({"user" : user_id})
      .sort({"created_at" : -1})
    return self._query_to_json_dict(_todos)

  def find_by_id_and_user(self, todo_id, user_id):
    return self._query_to_json_dict(self.todos.find(
      {"id" : todo_id, 
       "user" : user_id}))

  def find_model_by_id_and_user(self, todo_id, user_id):
    """Struggled with realizing how to query by model - 
      realized it was conn.[Model]. Hence this method 
      separate from the dict based ones. """
    
    return self.todos.MongoTodo.find_one(
      {"id" : todo_id, 
       "user" : user_id})

  def find_by_id(todo_id):
    return self._query_to_json_dict(self.todos.find_one(
      {"id" : todo_id}))
    
  def get(todo_id, user_id = None):
    """gets a todo. Validates user if passed"""
    if user_id:
      if not self.ensure_user(user_id):
        return None

      return self.find_by_id_and_user(todo_id, user_id)
    
    return self.find_by_id(todo_id)

  def delete(self, todo_id, user_id = None):
    """Removes a todo from the db. Validates user if passed"""

    todo = None
    if user_id:
      if not self.ensure_user(user_id):
        return None

      todo = self.find_by_id_and_user(todo_id, user_id)
    else:
      todo = self.find_by_id(todo_id)
    
    if todo:
      if len(todo) == 0:
        todo = None
      else:
        todo = todo[0]
        self.todos.remove({"id" : todo_id})

    return todo

  def create_todo(self, user, text):
    todo = self.todos.MongoTodo()
    todo.initialize(text, str(user))

    return todo

class User(Document):
  structure = {
    "name" : str,
    "identifier" : str
  }
  use_dot_notation = True

  def __repr__(self):
    return "User - %s" % self['name']

  def usr_id(self):
    return self['identifier']

  def initialize(self, name = None):
    uuid = shortuuid.ShortUUID().random(length=16)
    self.update(name, uuid)

  def update(self, name, identifier):
    """Updates user internal data. 

    Identifier should only updated when testing"""

    self['name'] = name
    self['identifier'] = identifier
    self.save()

class Priority(Enum):
  low = 1
  med = 2
  high = 3
  urgent = 4

class MongoTodo(Document):
  """Uses non-mongoid identifiers because
  ObjectId's are unwieldy"""

  structure = {
    "id" : str,
    "text" : unicode,
    "done" : bool,
    "user" : str,
    "priority" : int,
    "created_at" : datetime.datetime
  }

  use_dot_notation = True

  @staticmethod
  def mongo_to_json_dict(mongo_dict):
    del mongo_dict['_id']
    return mongo_dict

  def to_json_dict(self):
    return MongoTodo.mongo_to_json_dict(dict(self))

  def initialize(self, text, user):
    """Creates a new todo post
    Created as separate function to 
    ensure right arguments passed and
    makes sure fields names are only visible
    on the Mongo model. """

    self['user'] = user
    self['done'] = False
    self['priority'] = Priority.low
    uuid = shortuuid.ShortUUID().random(length=32)
    self['id'] = uuid
    self['created_at'] = datetime.now()

    self.update(text)

  def update(self, text = None, done = None, priority = None):
    """updates the editable fields on the todo"""

    do_update = text != None or done != None or priority != None
    if do_update:
      if text != None:
        self['text'] = text
      if done != None:
        self['done'] = done
      if priority != None:
        self['priority'] = priority

      #There's some type confusion here, stopgap solution
      self['id'] = str(self['id'])
      self['user'] = str(self['user'])

      self.save()

  def toggle_done(self):
    
    done = not self['done']
    self.update(None, done, None)

  def increase_priority(self):
    if self['priority'] < Priority.urgent:
      self.update(None, None, self['priority'] + 1)

  def decrease_priority(self):
    if self['priority'] > Priority.low:
      self.update(None, None, self['priority'] - 1)

  def __repr__(self):
    return "%s - %s" % (self['id'], self['text'])
