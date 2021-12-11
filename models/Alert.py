from . import db, ma


class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.BigInteger, primary_key=True)
    _metadata = db.Column("metadata", db.JSON, nullable=False)
    task_id = db.Column(db.BigInteger, db.ForeignKey('tasks.id'))

    def __init__(self, metadata):
        self._metadata = metadata


class TasksSchema(ma.Schema):
    class Meta:
        fields = ('id', 'status', 'start', 'end', 'weight_id')


class AlertsSchema(ma.Schema):
    tasks = ma.Nested(TasksSchema, many=True)

    class Meta:
        fields = ('id', 'metadata', 'description', 'task')


alert_schema = AlertsSchema()
alerts_schema = AlertsSchema(many=True)
