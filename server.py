import json
import os
import time
from flask import Flask, Response, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect, Namespace
import eventlet
eventlet.monkey_patch()

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

active_users = {}


class Chat(Namespace):
    def on_disconnect(self):
        print('Client disconnected', request.sid)
        if request.sid in active_users:
            del active_users[request.sid]

    def on_register(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        if request.sid in active_users:
            emit('register', {'data': 'failed', 'reason': 'already_connected'})
            print 'ERROR: User already registered!'
        elif message['data'] in active_users.values():
            emit('register', {'data': 'failed', 'reason': 'nickname_occupied'})
            print 'ERROR: Nickname already taken!'
        else:
            active_users[request.sid] = message['data']
            emit('register', {'data': 'success'})

    def on_my_msg(self, message):
        if request.sid not in active_users:
            return  # ERROR: user not registered
        with open('comments.json', 'r') as f:
            comments = json.loads(f.read())

        new_comment = message['data']
        new_comment['author'] = active_users[request.sid]
        new_comment['id'] = int(time.time() * 1000)
        comments.append(new_comment)

        with open('comments.json', 'w') as f:
            f.write(json.dumps(comments, indent=4, separators=(',', ': ')))

        session['receive_count'] = session.get('receive_count', 0) + 1

        emit('my_response', {'data': comments, 'count': session['receive_count']}, broadcast=True)


socketio.on_namespace(Chat('/api/chat'))

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    socketio.run(app, port=int(os.environ.get("PORT", 3000)), debug=True)
