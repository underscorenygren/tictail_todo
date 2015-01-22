(function() {

  var todos = [], 
      usr_id = 'test';

  function todo_model(api_data) {

    return {
      done : function() {
        return api_data['done'] ? true : false;
      }, 
      text : function() {
        return api_data['text'];
      }, 
      user : function() {
        return api_data['user'];
      },
      prio : function() {
        return api_data['priority'];
      },
      id : functino() {
        return api_data['id'];
      }
    }
  }

  function _url(endpoint) {
    return "" + usr_id + "/" + endpoint;
  }

  function _todo_url(todo_id, endpoint) {
    return _url("" + todo_id + "/" + endpoint);
  }

  function load_todos() {
    $.getJSON(_url('todos'), function(data) {
      todos = data;
      update_ui();
    });
  }

  function ajax_wrapper($elem, endpoint, 
                        todo_id callback) {
    var url = _todo_url(todo_id, endpoint),

    $elem.click(function() {
      $.post(url, function(data) { 
        console.log(data);
        if (callback) {
          callback(data);
        }
        update_ui();
      });
    );
  }

  function todo_to_jq(_todo) {
    var todo = todo_model(_todo),
        id = todo.id(),
        $todo = $("<div id='todo-" + id + 
                  "'></div>"),
        $inc = $("<a href='#' class='inc-prio'>+ Prio</a>"),
        $dec = $("<a href='#' class='dec-prio'>- Prio</a>"),
        $del = $("<a href='#' class='delete'>Delete</a>"),
        $done = $("<a href='#' class='done-btn'>(un)Done</a>");

    if (todo.done()) {
      $todo.addClass('done');
    }
    if (todo.prio()) {
      $todo.addClass('prio-' + todo.prio);
    }
    $todo.text(todo.text());

    ajax_wrapper($inc, todo_id, 'incprio');
    ajax_wrapper($dev, todo_id, 'decprio');
    ajax_wrapper($del, todo_id, 'delete');
    ajax_wrapper($done, todo_id, 'done');

    $todo.append($done);
    $todo.append($inc);
    $todo.append($dev);
    $todo.append($del);

    return $todo;
  }

  function update_ui() {

    var $todo_root = $('#todo_root')
        $inserter = $('<div id=\'todo_root\'></div>');

    for (var i = 0, il = todos.length; i < il; i++) {

      var todo = todos[i],
          $todo = todo_to_jq(todo);

      $inserter.append($todo);
    }

    $todo_root.replaceWith($inserter);

    }

  }

  $(document).ready(function() {

    load_todos();
  });

})();
