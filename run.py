from iotServer import app, socketio

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')
    #app.run()
    #host='0.0.0.0'