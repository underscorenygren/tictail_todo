from flask import Flask
import sys, os
from mongokit import Connection

from flask import render_template, jsonify, \
  redirect, url_for
from todo import TodoORM

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'tictailtodo'

class TodoApp(Flask):

  def connect_to_db(self, db_name = MONGO_DB):
    self.conn = Connection(MONGO_HOST, MONGO_PORT)
    self.db = self.conn[db_name]
    self.todo_orm = TodoORM(self.conn, self.db)

app = TodoApp(__name__)
app.debug = True
app.connect_to_db()

def render_view(file_name, variables, code = 200):
  return render_template(file_name, **variables)

def render_html(view_name, variables, code = 200):
  return render_view("%s.html" % view_name, variables)

def render_404():
  return render_html('404', {}, 404)

@app.route("/")
def index():
  """Creates an empty user and redirects to 
  it if usr does not exist"""
  new_usr = app.todo_orm.create_user()

  return redirect(
    url_for('todos',  **{'user_id' : new_usr.usr_id()}))

@app.route("/<user_id>/todos")
def todos(user_id):
  if not app.todo_orm.ensure_user(user_id):
    return render_404()

  output = app.todo_orm.all_by_user(user_id)
  return jsonify({"todos" : output})

@app.route("/<user_id>/todo/create", methods=['POST'])
def create(user_id):
  todo = app.todo_orm.create_todo(user_id, u"test")

  return jsonify(todo.to_json_dict())

@app.route("/<user_id>/todo/<todo_id>/delete", methods=['POST'])
def delete(user_id, todo_id):
  deleted = app.todo_orm.delete(todo_id, user_id)

  if deleted:
    return jsonify(deleted)
  else:
    return jsonify({"msg" : "No todo to delete"})

if __name__ == "__main__":
  
  app.run()
