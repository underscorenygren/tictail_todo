(function() {

  var todos = [];

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
      id : function() {
        return api_data['id'];
      }
    }
  }

  function _url(endpoint) {
    return "" + endpoint;
  }

  function _todo_url(todo_id, endpoint) {
    return _url("todo/" + todo_id + "/" + endpoint);
  }

  function load_todos() {
    $.getJSON(_url('todos'), function(data) {
      todos = data['todos'];
      update_ui();
    });
  }

  function ajax_wrapper($elem, endpoint, 
                        todo_id, data_callback) {
    var url;
    
    if (todo_id) {
      url = _todo_url(todo_id, endpoint);
    } else {
      url = _url(endpoint);
    }

    $elem.click(function() {
      var data = null;
      if (data_callback) { 
        data = data_callback();
      }

      $.post(url, data, function(_data) { 
        console.log(_data);
        load_todos();
      });
    });
  }

  function replace_with_input(todo, $text) {

    var $editor = $('<input class="text_input"></input>'),
        url = _todo_url(todo.id(), 'text');

    $editor.val(todo.text());
    $editor.keyup(function(evt) { 
      if (evt.keyCode == 13) {//enter
      
        $.post(url, 
          {"text" : 
            $editor.val()}, 
          function(_data) { 
              console.log(_data);
              load_todos();
          });
      } else if (evt.keyCode == 27) { //escape
        //Resets ui without changes
        load_todos();
      }
    });

    $text.replaceWith($editor);
  }

  function todo_to_jq(_todo) {
    var todo = todo_model(_todo),
        id = todo.id(),
        $controls = $("<td class='controls'></td>"),
        $todo = $("<tr id='todo-" + id + 
                  "' class='todo'></tr>"),
        $inc = $("<a href='#' class='todoctrl inc-prio'>more</a>"),
        $dec = $("<a href='#' class='todoctrl dec-prio'>less</a>"),
        $del = $("<a href='#' class='todoctrl delete'>delete</a>"),
        $done = $("<a href='#' class='todoctrl done-btn'>" + 
          (todo.done() ? "not&nbsp;done" : "done") + "</a>"),
        $text = $("<div></div>"),
        $text_td = $('<td class="text"></td>');


    if (todo.done()) {
      $text.addClass('done');
    }
    if (todo.prio()) {
      $text.addClass('prio-' + todo.prio());
    }

    $text.text(todo.text());
    $text_td.click(function() {
      replace_with_input(todo, $text)
    });

    ajax_wrapper($inc, 'incprio', id);
    ajax_wrapper($dec, 'decprio', id);
    ajax_wrapper($del, 'delete', id);
    ajax_wrapper($done, 'done', id);

    $todo.append($text_td.append($text));
    $controls.append($done);
    $controls.append($inc);
    $controls.append($dec);
    $controls.append($del);
    $todo.append($controls);

    return $todo;
  }

  function update_ui() {

    var $todo_root = $('#todo_root')
        $inserter = $('<table id=\'todo_root\'></table>');

    for (var i = 0, il = todos.length; i < il; i++) {

      var todo = todos[i],
          $todo = todo_to_jq(todo);

      $inserter.append($todo);
    }

    $todo_root.replaceWith($inserter);

  }

  function get_and_clear_input() {
    var $inp = $("#new_input"), 
        val = $inp.val();

    $inp.val('');
    return val;
  }

  $(document).ready(function() {
    ajax_wrapper($('#newtodo'), 'todo/create', false, 
      function() {
        return {"text": get_and_clear_input()};
      });
    load_todos();
    $('#new_input').focus();
  });

})();
