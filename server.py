import json
import os
import time
from flask import Flask, Response, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect, Namespace
from flask.ext.pymongo import PyMongo
from pymongo import GEO2D
from bson import json_util
from bson.son import SON
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
            mongo.db.users.insert({
                "id": request.sid,
                "nickname": message['data'],
                "loc": [message['lat'], message['lng']]
                # "loc": {
                #     "lat": message['lat'],
                #     "lng": message['lng']
                # }
            })
            mongo.db.users.create_index([("loc", GEO2D)])
            print "User", message['data'], "successfully registered with lat=", message['lat'], "lng=", message['lng']
            emit('register', {'data': 'success'})

    def on_my_msg(self, message):
        if mongo.db.users.find({"id": request.sid}).count() == 0:
            return  # ERROR: user not registered

        new_comment = message['data']
        user = mongo.db.users.find_one({"id": request.sid})
        new_comment['author'] = user['nickname']
        new_comment['id'] = int(time.time() * 1000)
        mongo.db.comments.insert(new_comment)
        neighbours = mongo.db.command(SON({
            'geoNear': "users",
            'near': user['loc']
        }))
        print neighbours["results"]

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
