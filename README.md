# tictail_todo

This coding experiment showcases a simple todo application using Flask backed by Mongo and a jQuery front end. It handles creating, updating and completing todos for unauthenticated but obfuscated users.

Installation
======

Install mongo
Install python
install dependencies:
pip install flask
pip install mongokit
pip install shortuuid
pip install enum

Running
=====

`python server.py`

Features
===

Handles users using URLs only, an obfuscated url is automatically greated when user hits the site and siloes the user without need for login. 

Persisent storage of todos on server using mongo. 

Prioritization of todos using a simple priority system, which signals important using font-size. 
Completion and Deletion of todos.

A Flask-integrated unittesting suite. 

Testing
=====

`python app_tests.py`

Approach
======

I decided to use Flask because it was what was recommended by @martinmelin. I haven't done app development in a while since hanging around Ruby for a year and change, so I was interested to see how it held up against Sinatra. 

For the front end, I decided against using React and went with jQuery. Aside from a few talks and articles, I'm not very familiar with the React framework. Given the light data-synchronization load and the time constraint, I decided to go with something I knew well and that I could bash out quickly. 

The back end is a straight forward flask app powered by mongo. I went with Mongo not for any particular data need, but because it's my most recent DB and I figured it would make it easier. I decided to use the mongokit ORM for python, thinking that since there were no performance bottlenecks I would save time handling their models. In the end, it had a few python-specific idiosynchrazies and wasn't as well documented as it initially seemed. Were I to do it again, I'm not sure I would recommend using it. 

Because I was running short on time, I decided against complicating the front end too much. Now, the client pings back to the server with every update of any todo, and redraws the whole UI each time. The client maintains no state other than a local cache of the server data, and with each redraw it calls to the server for the latest update. I went with this approach because it eliminated a lot of complexity on the client and I figured the calls would be fast enough that UI artifacts would not be an issue. Naturally, this approach would not scale particularly well as the data (and users) grow, as the latency of the server calls would no longer be instantaneous. As such, at that point I would move the data models over to a more sophisticated local cache an use React to handle the redraws. 

The endpoint do not come with any security, aside from what is provided by the libraries (`jQuery.text()` escapes html entities for example). Furthermore, there is no CSRF protection to keep user data safe. Once again, I chose to not spend time validating because I didn't consider it important for this excercise. Flask probably comes with some CSRF and/or sanitization facilities, which would be on the top list of features to add. 

When I originally designed the datamodel I went with a simple fixed integer priority system. Instead of sorting todos manually, I wanted to see what it would feel like if higher priority elements were bolder, instead of changing their position in the stream. The thinking is that if you cannot change the order of your todos, only make them larger and finish them, perhaps you would finish things differently. I decided against supporting re-organization of the stream client side, and I thought the result was somewhat compelling. With this approach, maintaining all state server side was eaven easier, since I would never have to worry about the order of the resulting todo list changing. 

I've always been interested in webapps that create anonymous users on the client's behalf, and then gives them a siloes space for edits that they can only access with the unique URL. Hence, I mirrored this approach. My implementation is a bit too simplistic - aside from XSS concerns, it doesn't do any deletion/maintenance of dummy users that have been created without being interacted with. This could be easily handled by a cron that checks for users without todos and deletes them, but once again I didn't feel any need to focus on that in this experiment. 


