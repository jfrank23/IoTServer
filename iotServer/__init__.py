import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO



app = Flask(__name__)
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


from iotServer import routes
