from flask import request, jsonify
import json
from models.Weight import *
from models.Camera import *
from models.Event import *
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_lists():
    data = json.loads(request.args.get('lists'))

    results = {}
    
    for item in data:
        if item == 'cameras':
            result = Camera.query.all()
            results[item] = cameras_schema.dump(result)

        if item == 'weights':
            result = Weight.query.all()
            results[item] = weights_schema.dump(result)

        if item == 'labels':
            result = db.session.query(Weight.classes).distinct()
            results[item] = weights_schema.dump(result)

    return jsonify({'lists': results})
