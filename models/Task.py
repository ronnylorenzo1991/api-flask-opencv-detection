from . import db, ma
from sqlalchemy.dialects.mysql import TIME

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.String(10))
    start = db.Column(TIME())
    end = db.Column(TIME())
    alerts = db.relationship("Alert", backref=db.backref('task'))
    weight_id = db.Column(db.BigInteger, db.ForeignKey('weights.id'))
    camera_id = db.Column(db.BigInteger, db.ForeignKey('cameras.id'))

    def __init__(self, status, start, end):
        self.status = status
        self.start = start
        self.end = end

class CameraSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'url', 'activated')

class WeightSchema(ma.Schema):
    class Meta:
        fields = ('id', 'filename', 'description', 'classes')

class AlertSchema(ma.Schema):
    class Meta:
        fields = ('id', 'metadata')

class TaskSchema(ma.Schema):
    camera = ma.Nested(CameraSchema)
    weight = ma.Nested(WeightSchema)
    alerts = ma.Nested(AlertSchema, many=True)
    class Meta:
        fields = ('id', 'status', 'start', 'end', 'camera', 'weight', 'alerts')

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
