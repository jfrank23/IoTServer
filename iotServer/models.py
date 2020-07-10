from iotServer import db
from datetime import datetime

class Device(db.Model):
    mac = db.Column(db.Text, primary_key=True)
    ip = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    devType = db.Column(db.Text, nullable=False)
    fields = db.relationship("Field",backref='device',lazy=True)

class Field(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.Text,nullable = False)
    unit = db.Column(db.Text,nullable=False)
    method = db.Column(db.Text, nullable=True)
    deviceMac = db.Column(db.Text, db.ForeignKey('device.mac'),nullable=False)
    readings = db.relationship("Reading",backref='field',lazy=True)

class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timePosted = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    reading = db.Column(db.Float, nullable = False)
    fieldId = db.Column(db.Integer, db.ForeignKey('field.id'),nullable=False)
    deviceMac = db.Column(db.Text, db.ForeignKey('device.mac'),nullable=False)
