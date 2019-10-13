import json

from flask import Flask
from flask import request
from flask import render_template
from geventwebsocket.server import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocket

web_app = Flask(__name__)

user_socket_dict = {}  # {user_id: wsgi.websocket}


@web_app.route("/")
def web_toy():
    return render_template("webToy.html")


@web_app.route("/app/<user_id>")
def app(user_id):
    app_socket = request.environ.get("wsgi.websocket")  # type: WebSocket
    if app_socket:
        user_socket_dict[user_id] = app_socket

    while True:
        app_data = app_socket.receive()
        app_data_dict = json.loads(app_data)
        to_user = app_data_dict.get("to_user")
        to_app_socket = user_socket_dict.get(to_user)
        to_app_socket.send(app_data)


@web_app.route("/toy/<toy_id>")
def toy(toy_id):
    toy_socket = request.environ.get("wsgi.websocket")  # type: WebSocket
    if toy_socket:
        user_socket_dict[toy_id] = toy_socket

    while True:
        toy_data = toy_socket.receive()
        toy_data_dict = json.loads(toy_data)
        to_user = toy_data_dict.get("to_user")
        to_toy_socket = user_socket_dict.get(to_user)
        to_toy_socket.send(toy_data)


if __name__ == "__main__":
    http_serve = WSGIServer(("0.0.0.0", 8000), web_app, handler_class=WebSocketHandler)
    http_serve.serve_forever()
