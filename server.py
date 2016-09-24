import json
import os
import time
from flask import Flask, Response, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect, Namespace
from flask.ext.pymongo import PyMongo
from bson import json_util
import eventlet
eventlet.monkey_patch()

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

mongo = PyMongo(app)

async_mode = None
socketio = SocketIO(app, async_mode=async_mode)


class Chat(Namespace):

    def on_disconnect(self):
        print('Client disconnected', request.sid)
        if mongo.db.users.find({"id": request.sid}):
            mongo.db.users.remove({"id": request.sid})

    def on_register(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        if mongo.db.users.find({"id": request.sid}).count() > 0:
            emit('register', {'data': 'failed', 'reason': 'already_connected'})
            print 'ERROR: User already registered!'
        elif mongo.db.users.find({"nickname": message['data']}).count() > 0:
            emit('register', {'data': 'failed', 'reason': 'nickname_occupied'})
            print 'ERROR: Nickname already taken!'
        else:
            mongo.db.users.insert({"id": request.sid, "nickname": message['data']})
            emit('register', {'data': 'success'})

    def on_my_msg(self, message):
        if mongo.db.users.find({"id": request.sid}).count() == 0:
            return  # ERROR: user not registered

        new_comment = message['data']
        new_comment['author'] = mongo.db.users.find_one({"id": request.sid})['nickname']
        new_comment['id'] = int(time.time() * 1000)
        mongo.db.comments.insert(new_comment)

        session['receive_count'] = session.get('receive_count', 0) + 1

        comments_data = tuple(mongo.db.comments.find())
        comments_data = json.dumps(comments_data, default=json_util.default, separators=(',', ':'))
        comments_data = json.loads(comments_data)

        emit('my_response', {'data': comments_data, 'count': session['receive_count']}, broadcast=True)


socketio.on_namespace(Chat('/api/chat'))

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    socketio.run(app, port=int(os.environ.get("PORT", 3000)), debug=True)
