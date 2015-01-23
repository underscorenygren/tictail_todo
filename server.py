from flask import Flask
import sys, os
from mongokit import Connection

from flask import render_template, jsonify, \
  redirect, url_for, request
from todo import TodoORM

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'tictailtodo'

class TodoApp(Flask):

  def connect_to_db(self, db_name = MONGO_DB):
    self.conn = Connection(MONGO_HOST, MONGO_PORT)
    self.db = self.conn[db_name]
    self.todo_orm = TodoORM(self.conn, self.db)

app = TodoApp(__name__, static_url_path='')
app.debug = True
app.connect_to_db()

def render_view(file_name, variables, code = 200):
  return render_template(file_name, **variables)

def render_html(view_name, variables, code = 200):
  return render_view("%s.html" % view_name, variables)

def render_404():
  return render_html('404', {}, 404)

@app.route('/ui.js')
def uijs():
  f = app.send_static_file('ui.js')
  return f

@app.route('/reset.css')
def resetcss():
  return app.send_static_file('reset.css')

@app.route("/")
def index():
  """Creates an empty user and redirects to 
  it if usr does not exist"""
  new_usr = app.todo_orm.create_user()

  return redirect(
    url_for('user_root_classic',  **{'user_id' : new_usr.usr_id()}))

@app.route("/<user_id>/")
def user_root(user_id):
  if not app.todo_orm.ensure_user(user_id):
    return render_404()

  return render_html('todos', {})

@app.route("/<user_id>/classic")
def user_root_classic(user_id):
  if not app.todo_orm.ensure_user(user_id):
    return render_404()

  return render_html('sleekui', {})

@app.route("/<user_id>/todos")
def todos(user_id):
  if not app.todo_orm.ensure_user(user_id):
    return jsonify({"todos" : []})

  output = app.todo_orm.all_by_user(user_id)
  output.reverse()
  return jsonify({"todos" : output})

@app.route("/<user_id>/todo/create", methods=['POST'])
def create(user_id):
  try: 
    text = request.form['text']
  except KeyError:
    return jsonify({"msg" : "No text passed to create!"});

  todo = app.todo_orm.create_todo(user_id, text)

  return jsonify(todo.to_json_dict())

@app.route("/<user_id>/todo/<todo_id>/get")
def get_todo(user_id, todo_id):
  todo = app.todo_orm.find_model_by_id_and_user(todo_id, user_id)

  if not todo:
    return jsonify({"msg" : "No todo with that id"})

  return jsonify(todo.to_json_dict())

@app.route("/<user_id>/todo/<todo_id>/text", methods=['POST'])
def update_text(user_id, todo_id):
  todo = app.todo_orm.find_model_by_id_and_user(todo_id, user_id)
  
  if not todo:
    return jsonify({"msg" : "No todo with that id"})

  text = request.form['text']
  todo.update(text)

  return jsonify(todo.to_json_dict())

@app.route("/<user_id>/todo/<todo_id>/move", methods=['POST'])
def update_pos(user_id, todo_id):
  todo = app.todo_orm.find_model_by_id_and_user(todo_id, user_id)
  
  if not todo:
    return jsonify({"msg" : "No todo with that id"})

  todo.set_position(int(request.form['pos']))

  return jsonify(todo.to_json_dict())

@app.route("/<user_id>/todo/<todo_id>/done", methods=['POST'])
def done(user_id, todo_id):
  todo = app.todo_orm.find_model_by_id_and_user(todo_id, user_id)
  
  if not todo:
    return jsonify({"msg" : "No todo with that id"})
  
  todo.toggle_done()

  return jsonify(todo.to_json_dict())

@app.route("/<user_id>/todo/<todo_id>/incprio", methods=['POST'])
def incprio(user_id, todo_id):
  todo = app.todo_orm.find_model_by_id_and_user(todo_id, user_id)
  
  if not todo:
    return jsonify({"msg" : "No todo with that id"})
  
  todo.increase_priority()

  return jsonify(todo.to_json_dict())

@app.route("/<user_id>/todo/<todo_id>/decprio", methods=['POST'])
def devprio(user_id, todo_id):
  todo = app.todo_orm.find_model_by_id_and_user(todo_id, user_id)
  
  if not todo:
    return jsonify({"msg" : "No todo with that id"})
  
  todo.decrease_priority()

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
