from flask import Flask, Blueprint
from flask_sockets import Sockets
from flask import request
import psycopg2
import random, string

print(1)
conn = psycopg2.connect(
    host="free-tier14.aws-us-east-1.cockroachlabs.cloud",
    database="bitcamp-hack-1163.defaultdb",
    user="danny",
    password="bfoniXZ9evI3uRqe4R2vVw",
    port="26257")

cur = conn.cursor()
cur.execute('SELECT version()')
db_version = cur.fetchone()
print(db_version)

html = Blueprint(r'html', __name__)
ws = Blueprint(r'ws', __name__)

rooms = {}

@ws.route('/echo')
def echo_socket(socket):
    while not socket.closed:
        message = str(socket.receive())
        if message.startswith('create_room:'):
            # create_room:<username>
            code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
            rooms[code] = [{'username' : message.replace('create_room:', ''), 'socket' : socket}]
            socket.send(code)
        elif message.startswith('join_room:'):
            # join_room:<username>:<code>
            rooms[message.split(':')[2]].append({'username' : message.split(':')[1], 'socket' : socket})
            
            socket.send('{}'.format(list(map(lambda x: x['username'], rooms[message.split(':')[2]]))))
        else:
            # <code>:<username>:<message>
            print('message received: ' + message)
            code = message.split(':')[0]
            username = message.split(':')[1]
            message = message.split(':')[2]
            for sock in rooms[code]:
                sock['socket'].send(username + ':' + message)
        print(rooms)


app = Flask(__name__,
            static_url_path='',
            static_folder='')
sockets = Sockets(app)

@app.route('/user', methods=['GET', 'POST'])
def user():
    print(query := "SELECT * from users WHERE username='{}';".format(request.args.get('username')))
    cur.execute(query)
    return 'hello: {}'.format(cur.fetchone())

@app.route('/signup', methods=['POST'])
def signup():
    query = "INSERT INTO users (username, password, profile_img, display_name) VALUES ('{}', '{}', '{}', '{}');".format(
        request.form.get('username'),
        request.form.get('password'),
        request.form.get('profile_img'),
        request.form.get('display_name')
    )
    print(query)
    success = cur.execute(query)
    return 'success: {}, try to <a href="/index.html">log in</a>'.format(success is None)

@app.route('/login', methods=['POST'])
def login():
    print(query := "SELECT * from users WHERE username='{}' AND password='{}';".format(request.form.get('username'), request.form.get('password')))
    cur.execute(query)
    info = cur.fetchone()
    res = app.make_response('')
    res.set_cookie("username", value=info[0])
    res.set_cookie("password", value=info[1])
    res.set_cookie("profile_img", value=info[2])
    res.set_cookie("display_name", value=info[3])
    res.headers['location'] = '/createparty.html'

    return res, 302
    # return '{}'.format()

app.register_blueprint(html, url_prefix=r'/')

sockets.register_blueprint(ws, url_prefix=r'/')


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('127.0.0.1', 8000), app, handler_class=WebSocketHandler)
    # server = pywsgi.WSGIServer(('0.0.0.0', 443), app, keyfile='privkey.pem', certfile='fullchain.pem', handler_class=WebSocketHandler)
    server.serve_forever()
