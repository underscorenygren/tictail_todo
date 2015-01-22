from flask import Flask
import sys, os

from flask import render_template, jsonify
from slimish_jinja import SlimishExtension
from todo import Todo

class TodoApp(Flask):
  jinja_options = Flask.jinja_options
  jinja_options['extensions'].append(SlimishExtension)

app = TodoApp(__name__)
app.debug = True

todos_arr = []

def render_view(file_name, variables):
  return render_template(file_name, **variables)

def render_slim(view_name, variables):
  return render_view("%s.slim" % view_name, variables)

def render_html(view_name, variables):
  return render_view("%s.html" % view_name, variables)

@app.route("/")
def index():
  return render_html('index', 
    {"content": "Hello, world"})

@app.route("/todos")
def todos():
  output = [todo.to_json_dict() for todo in todos_arr]
  return jsonify({"todos" : output})

@app.route("/create", methods=['POST'])
def create():
  todo = Todo("test")
  todos_arr.append(todo)

  return jsonify(todo.to_json_dict())


  

if __name__ == "__main__":
  
  app.run()
