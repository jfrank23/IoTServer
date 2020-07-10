from flask import render_template, request, jsonify
from iotServer.models import Device, Field, Reading
from datetime import datetime
from iotServer import app, db

@app.route('/', methods=['GET'])
def index_page_landing():
    return render_template("layout.html")


# ------------------API-------------------------------

@app.route('/api/v1/setupDevice', methods=['POST'])
def setupDevice():
    if 'mac' in request.json and 'ip' in request.json and 'name' in request.json and 'devType' in request.json:
        if type(request.json['mac']) == str and type(request.json['ip']) == str and type(
                request.json['name']) == str and type(request.json['devType']) == str:
            device = Device(mac=request.json['mac'], ip=request.json['ip'], name=request.json['name'],
                            devType=request.json['devType'])
            existingDevice = Device.query.filter_by(mac=device.mac).first()
            if not existingDevice:
                db.session.add(device)
                db.session.commit()
                return "created"
            else:
                return "already exists", 302
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
        reading = Reading()
        device = Device.query.filter_by(mac=request.json['deviceMac']).first()
        fields = device.fields
        for field in fields:
            if field.name in request.json and type(request.json[field.name]) == float:
                reading.deviceMac = request.json['deviceMac']
                reading.fieldId = field.id
                reading.timePosted = datetime.now()
                reading.reading = request.json[field.name]
                db.session.add(reading)
                db.session.commit()
                count += 1
        if count:
            return "posted", 200
    return "error", 400