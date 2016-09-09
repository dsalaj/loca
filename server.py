import json
import os
import time
from flask import Flask, Response, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import eventlet
eventlet.monkey_patch()

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
thread = None
namespace = '/api/comments'


@app.route(namespace, methods=['GET', 'POST'])
def comments_handler():
    with open('comments.json', 'r') as f:
        comments = json.loads(f.read())

    if request.method == 'POST':
        new_comment = request.form.to_dict()
        new_comment['id'] = int(time.time() * 1000)
        comments.append(new_comment)

        with open('comments.json', 'w') as f:
            f.write(json.dumps(comments, indent=4, separators=(',', ': ')))

    return Response(
        json.dumps(comments),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )


# def background_thread():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         socketio.sleep(10)
#         count += 1
#         socketio.emit('my_response',
#                       {'data': 'Server generated event', 'count': count},
#                       namespace=namespace)
#
#
# @socketio.on('connect', namespace=namespace)
# def test_connect():
#     global thread
#     if thread is None:
#         thread = socketio.start_background_task(target=background_thread)
#     emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace=namespace)
def test_disconnect():
    print('Client disconnected', request.sid)


@socketio.on('my_event', namespace=namespace)
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    message['data']['id'] = int(time.time() * 1000)
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_msg', namespace=namespace)
def form_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    message['data']['id'] = int(time.time() * 1000)
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    socketio.run(app, port=int(os.environ.get("PORT", 3000)), debug=True)
