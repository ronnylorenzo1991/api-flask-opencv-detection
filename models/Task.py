from . import db, ma
from sqlalchemy.dialects.mysql import TIME

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.String(10))
    start = db.Column(TIME())
    end = db.Column(TIME())
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

class TaskSchema(ma.Schema):
    camera = ma.Nested(CameraSchema)
    weight = ma.Nested(WeightSchema)
    class Meta:
        fields = ('id', 'status', 'start', 'end', 'camera', 'weight')

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
