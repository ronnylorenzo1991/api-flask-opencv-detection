from . import db, ma 

class Camera(db.Model):
    __tablename__ = 'cameras'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    url = db.Column(db.String(255), unique=True)
    activated = db.Column(db.Boolean, default=False)
    tasks = db.relationship("Task", backref=db.backref('camera'))
    events = db.relationship("Event", backref=db.backref('camera'))

    def __init__(self, name, url, activated):
        self.name = name
        self.url = url
        self.activated = activated

class TasksSchema(ma.Schema):
    class Meta:
        fields = ('id', 'status', 'start', 'end', 'weight_id')

class EventSchema(ma.Schema):
    class Meta:
        fields = ('id', 'number', 'description', 'classes', 'coordinates', 'source', 'score', 'image', 'date')

class CameraSchema(ma.Schema):
    tasks = ma.Nested(TasksSchema, many=True)
    events = ma.Nested(EventSchema, many=True)
    class Meta:
        fields = ('id', 'name', 'url', 'activated', 'tasks', 'events')

camera_schema = CameraSchema()
cameras_schema = CameraSchema(many=True)