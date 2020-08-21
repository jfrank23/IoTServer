from flask import render_template, request, jsonify, redirect
from iotServer.models import Device, Field, Reading
from iotServer.viewModels import DisplayDevice
from datetime import datetime, timedelta
from iotServer import app, db, socketio
import requests
import ipaddress

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def index_page_landing():
    current = datetime.now()
    devices = Device.query.filter_by();
    clientsToDisplay = []
    serversToDisplay =[]
    for dev in devices:
        if(dev.devType=="server"):
            displayDevice = DisplayDevice()
            displayDevice.cleanMac = "M" + dev.mac.replace(":", "")
            displayDevice.device = dev
            displayDevice.latestPost = latestPost
            displayDevice.fields = dev.fields
            serversToDisplay.append(displayDevice)
        else:
            latestPost = datetime.now() - timedelta(days=1)
            for field in dev.fields:
                temp = field.readings
                temp.sort(key=lambda x: x.timePosted, reverse=True)
                try:
                    temp = temp[0].timePosted
                except:
                    temp=datetime.now() - timedelta(days=1)
                if temp:
                    if temp > latestPost:
                        latestPost = temp
            if latestPost >( current.now() - timedelta(hours=1)):
                displayDevice= DisplayDevice()
                displayDevice.cleanMac = "M" + dev.mac.replace(":","")
                displayDevice.device= dev
                displayDevice.latestPost = latestPost
                displayDevice.fields = dev.fields
                clientsToDisplay.append(displayDevice)
    return render_template("index.html",clients=clientsToDisplay,servers=serversToDisplay)

@app.route('/client/<mac>', methods=['GET'])
def clientPage(mac):
    device=Device.query.filter_by(mac=mac).first()
    if device:
        return render_template("client.html", device=device)
    else:
        return render_template("404.html")


@app.route('/server/<mac>', methods=['GET'])
def serverPage(mac):
    device = Device.query.filter_by(mac=mac).first()
    if device:
        try:
            backwardsIP = str(ipaddress.IPv4Address(int(device.ip))).split('.')
            ip = '.'.join(backwardsIP[::-1])
            response = requests.get("http://" + ip + "/status")
        except:
            return render_template("404.html")

        return render_template("server.html", device=device, status=response.json())
    else:
        return render_template("404.html")

@app.route('/delete/<mac>', methods=['GET', 'POST'])
def serverDeletePage(mac):
    if request.method == 'POST':
        if request.form["delete_button"]=="Delete":
            device = Device.query.filter_by(mac=mac).first()
            fields = Field.query.filter_by(deviceMac = mac).all()
            readings = Reading.query.filter_by(deviceMac = mac).all()
            db.session.delete(device)
            for field in fields:
                db.session.delete(field)
            for reading in readings:
                db.session.delete(reading)
            db.session.commit()
            return redirect("/index.html")
    device = Device.query.filter_by(mac=mac).first()
    if device:
        return render_template("deleteServer.html", device=device)
    else:
        return render_template("404.html")
# --------------------API----------------------------

@app.route('/api/v1/setupDevice', methods=['POST'])
def setupDevice():
    if 'mac' in request.json and 'ip' in request.json and 'name' in request.json and 'devType' in request.json:
        if type(request.json['mac']) == str and type(request.json['ip']) == str and type(
                request.json['name']) == str and type(request.json['devType']) == str:
            device = Device(mac=request.json['mac'], ip=request.json['ip'], name=request.json['name'],
                            devType=request.json['devType'].lower())
            existingDevice = Device.query.filter_by(mac=device.mac).first()
            if not existingDevice:
                db.session.add(device)
                db.session.commit()
                return "created"
            else:
                existingDevice.ip = device.ip
                existingDevice.name = device.name
                existingDevice.devType = device.devType.lower()
                db.session.commit()
                return "Updated", 302
    return "error", 400


@app.route('/api/v1/addField', methods=['POST'])
def addField():
    if 'name' in request.json and 'unit' in request.json and 'deviceMac' in request.json:
        if type(request.json['name']) == str and type(request.json['unit']) == str and type(
                request.json['deviceMac']) == str:
            field = Field(name=request.json['name'], unit=request.json['unit'], deviceMac=request.json['deviceMac'])
            if 'method' in request.json and type(request.json['method']) == str:
                field.method = request.json['method']
            device = Device.query.filter_by(mac=field.deviceMac).first()
            existingField = Field.query.filter_by(deviceMac=device.mac, name=field.name).first()
            if device and not existingField:
                db.session.add(field)
                db.session.commit()
                return "created"
            elif existingField:
                return "field exists", 302
    return "error", 400


@app.route('/api/v1/data', methods=['POST'])
def recieveData():
    count = 0
    if 'deviceMac' in request.json and type(request.json['deviceMac']) == str:
        device = Device.query.filter_by(mac=request.json['deviceMac']).first()
        fields = device.fields
        print(request.json)
        for field in fields:
            if field.name in request.json and (type(request.json[field.name]) == float or type(request.json[field.name]) == int):
                reading = Reading()
                reading.deviceMac = request.json['deviceMac']
                reading.fieldId = field.id
                reading.timePosted = datetime.now()
                reading.reading = request.json[field.name]
                db.session.add(reading)
                db.session.commit()
                socketio.emit(str(reading.deviceMac),{field.name:reading.reading, 'Time' : str(reading.timePosted)})
                count += 1
        if count:
            return "posted", 200
    return "error", 400

#-------------------------------- Sockets----------------------------------
@socketio.on('post')
def handle_post(json):
    for key in json.keys():
        if key != 'ip':
            point = key
            break
    backwardsIP = str(ipaddress.IPv4Address(int(json["ip"]))).split('.')
    ip = '.'.join(backwardsIP[::-1])
    try:
        response = requests.post("http://" + ip + "/"+point, json={point: int(json[point])})
        if response.status_code == 200:
            socketio.emit('acceptedPost', json)
    except:
        pass
