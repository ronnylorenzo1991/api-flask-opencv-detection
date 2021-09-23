from . import db, ma


class Weight(db.Model):
    __tablename__ = 'weights'
    id = db.Column(db.BigInteger, primary_key=True)
    filename = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(50))
    classes = db.Column(db.JSON, nullable=False)
    tasks = db.relationship("Task", backref=db.backref('weight'))
    events = db.relationship("Event", backref=db.backref('weight'))
    
    def __init__(self, filename, description, classes):
        self.filename = filename
        self.classes = classes
        self.description = description

class TasksSchema(ma.Schema):
    class Meta:
        fields = ('id', 'status', 'start', 'end', 'weight_id')

class EventSchema(ma.Schema):
    class Meta:
        fields = ('id', 'number', 'description', 'classes', 'source', 'score', 'image', 'date')

class WeightSchema(ma.Schema):
    tasks = ma.Nested(TasksSchema, many=True)
    events = ma.Nested(EventSchema, many=True)
    class Meta:
        fields = ('id', 'filename', 'description', 'classes', 'tasks', 'events')


weight_schema = WeightSchema()
weights_schema = WeightSchema(many=True)
