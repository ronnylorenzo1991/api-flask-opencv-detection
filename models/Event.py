from . import db, ma

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.BigInteger, primary_key=True)
    number = db.Column(db.BigInteger, unique=True)
    description = db.Column(db.String(50))
    score = db.Column(db.Float(50))
    classes = db.Column(db.JSON, nullable=False)
    coordinates = db.Column(db.JSON, nullable=False)
    image = db.Column(db.String(20))
    date = db.Column(db.DateTime)
    weight_id = db.Column(db.BigInteger, db.ForeignKey('weights.id'))
    camera_id = db.Column(db.BigInteger, db.ForeignKey('cameras.id'))

    def __init__(self, number, description, classes, coordinates, score, image, date):
        self.number = number
        self.description = description
        self.classes = classes
        self.coordinates = coordinates
        self.score = score
        self.image = image
        self.date = date

class CameraSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'url', 'activated')

class WeightSchema(ma.Schema):
    class Meta:
        fields = ('id', 'filename', 'description', 'classes')


class EventSchema(ma.Schema):
    camera = ma.Nested(CameraSchema)
    weight = ma.Nested(WeightSchema)
    class Meta:
        fields = ('id', 'number', 'description', 'classes', 'coordinates', 'score', 'image', 'date', 'camera', 'weight')

event_schema = EventSchema()
events_schema = EventSchema(many=True)
