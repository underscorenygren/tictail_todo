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
      }, 
      pos : function() {
        return api_data['pos'];
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
//from: http://stackoverflow.com/questions/1771627/preventing-click-event-with-jquery-drag-and-drop
      if ($elem.hasClass('noclick')) {
        $elem.removeClass('noclick');
        return;
      }

      var data = null;
      if (data_callback) { 
        data = data_callback();
      }

      $.post(url, data, function(_data) { 
        console.log(_data);
        load_todos();
      });

      return false;
    });
  }

  function replace_with_input(todo, $text) {

    var $editor = $('<input class="text_input"></input>'),
        url = _todo_url(todo.id(), 'text');

    $editor.val(todo.text());
    $editor.keyup(function(evt) { 
      if (evt.keyCode === 13) {//enter
      
        $.post(url, 
          {"text" : 
            $editor.val()}, 
          function(_data) { 
              console.log(_data);
              load_todos();
          });
      } else if (evt.keyCode === 27) { //escape
        //Resets ui without changes
        load_todos();
      }
    });

    $editor.blur(function() {
      load_todos();
    });

    $text.replaceWith($editor);
    $editor.focus();
  }

  function todo_to_jq_classic(_todo, i) {

    var todo = todo_model(_todo),
        id = todo.id(),
        $todo = $("<div id='todo-" + id + 
                  "' class='todo'></div>"),
        $check = $('<input type="checkbox" class="form-control cbox">'),
        $text = $("<div class='text-div'></div>"), 
        even_odd = i % 2 == 0 ? 'even' : 'odd',
        $anchor = $('<span class="anchor glyphicon glyphicon-move"></span>');

    if (todo.done()) {
      $text.addClass('done');
      $check.attr('checked', 'checked');
    }
    $anchor.hide();

    $text.text(todo.text());
    $todo.addClass(even_odd);

    ajax_wrapper($todo, 'done', id);
    $todo.append($check);
    $todo.append($text);
    $todo.append($anchor);

    $todo.mouseover(function() {
      $anchor.show();
    }).mouseout(function() {
      $anchor.hide();
    });

    $todo.draggable({
       "handle" : ".anchor",
       "start" : function() {
          $(this).addClass('noclick');
        }});
    $todo.droppable({
      "drop" : function(evt, ui) {
        update_order(ui.draggable[0], this);
      }
    });

    return $todo;

  }

  function todo_to_jq_retro(_todo, i) {
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
      return false;
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

  var todo_to_jq = (function() { 
    var classic = window.CLASSIC_VIEW || false;
    if (classic) {
      return todo_to_jq_classic;
    } else {
      return todo_to_jq_retro;
    }
  })();

  function update_ui() {

    var $todo_root = $('#todo_root'),
        type = CLASSIC_VIEW ? 'div' : 'table',
        $inserter = $('<' + type + ' id=\'todo_root\'></' + type + '>'),
        n_done = 0, $n_left = $('#n_left'), 
        i, il;

    for (i = 0, il = todos.length; i < il; i++) {

      var todo = todos[i],
          $todo = todo_to_jq(todo, i);

      if (todo_model(todo).done()) {
        n_done += 1;
      }

      $inserter.append($todo);
    }
    $n_left.text(il - n_done);

    $todo_root.replaceWith($inserter);
  }

  function get_and_clear_input() {
    var $inp = $("#new_input"), 
        val = $inp.val();

    $inp.val('');
    return val;
  }

  function apply_on_all_todos(bool_check, 
                              endpoint, 
                              data_callback) {
    //This should really be solved with promises
    //But counting up and down is prob good enough
    var pending = 0;
    for (var i = 0, il = todos.length; i < il; i++) {
      var _todo = todos[i],
          todo = todo_model(_todo);

      if (bool_check(todo)) {
        var url = _todo_url(todo.id(), endpoint), 
            data = null;
        pending += 1;
        if (data_callback) {
          data = data_callback(todo);
        }
        $.post(url, data, function(_data) {
          pending -= 1;

          if (pending === 0) {
            load_todos();
          }

        });
      }
    }
  }

  function get_todo_model_from_elem($elem) {
    var dest_id = $elem.attr('id').substring(5),
        i, il, todo;

    for (i = 0, il = todos.length; i < il; i++) {
      todo = todo_model(todos[i]);

      if (todo.id() === dest_id) {
        return todo;
      }
    }

    return null;
  }

  function update_order(moved_elem, 
                        destination_elem) {

    var $dest = $(destination_elem), 
        dst_model = get_todo_model_from_elem($dest),
        dst_pos = dst_model.pos(), 
        moved_model = get_todo_model_from_elem($(moved_elem)),
        src_pos = moved_model.pos(),
        min_pos = Math.min(dst_pos, src_pos),
        max_pos = Math.max(dst_pos, src_pos);

    apply_on_all_todos(
      function(todo) {
        return todo.pos() >= min_pos && 
               todo.pos() <= max_pos;
      }, 
      'move',
      function(todo) {
        var new_pos;
        if (todo.pos() === src_pos) {
          new_pos = dst_pos;
        } else {
          if (src_pos > dst_pos) {
            new_pos = todo.pos() + 1
          } else {
            new_pos = todo.pos() - 1
          }
        }
  
        return {'pos' : new_pos};
      }
    );
  }


  $(document).ready(function() {
    var $newtodo = $('#newtodo');
    ajax_wrapper($newtodo, 'todo/create', false, 
      function() {
        return {"text": get_and_clear_input()};
      });

    $('#new_input').keyup(function(event) {
      
      if (event.keyCode == 13) {
        $newtodo.click();
      }
    });


    $('#delete_completed').click(function() {
      apply_on_all_todos(
        function(todo) {
          return todo.done();
        }, 
        'delete'
      );

      return false;
    });

    $('.all_complete').click(function() {
      apply_on_all_todos(
        function(todo) {
          return !todo.done();
        },
        'done'
      );
      
      return false;
    });

    load_todos();
    $('#new_input').focus();
  });

})();
