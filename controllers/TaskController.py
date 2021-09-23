from models.Camera import Camera
from models.Weight import Weight
from sqlalchemy.sql.expression import text
from flask import request, jsonify
from sqlalchemy import exc
from models.Task import *
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_all():
    sort = request.args.get('sort').split("|")
    sort_dir = text(sort[0] + " " + sort[1]) if sort[0] else text('id desc')
    per_page = int(request.args.get('per_page'))
    page = int(request.args.get('page'))
    total = Task.query.count()
    tasks = Task.query.order_by(sort_dir).paginate(
        page, per_page, error_out=False)
    result = tasks_schema.dump(tasks.items)
    offset = (page - 1) * per_page
    item_from = offset + 1
    item_to = offset + per_page
    if not tasks.has_next:
        item_to = total

    return jsonify({
        "total": total,
        "per_page": per_page,
        "current_page": page,
        "last_page": tasks.pages,
        "next_page_url": "",
        "prev_page_url": "",
        "from": item_from,
        "to": item_to,
        'data': result
    })

def create():
    wj_weight_id = request.form['weightId']
    wj_camera_id = request.form['cameraId']
    wj_start, wj_end = getTimeInterval(request.form['time'])

    weight = db.session.query(Weight).get(wj_weight_id)
    camera = db.session.query(Camera).get(wj_camera_id)

    task = Task(
        status = '1',
        start = wj_start,
        end = wj_end,
    )

    try:
        db.session.add(task)
        weight.tasks.append(task)
        camera.tasks.append(task)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        error = str(e.__dict__['orig'])
        return jsonify({'message': error, }), 400
    else:
        return jsonify({
            'message': 'Tarea Creada con éxito',
        })

def edit(id):
    weight = db.session.query(Weight).get(request.form['weightId'])
    camera = db.session.query(Camera).get(request.form['cameraId'])
    wj_start, wj_end = getTimeInterval(request.form['time'])
  
    task = db.session.query(Task).get(id)
    task.start = wj_start
    task.end = wj_end

    try:
        weight.tasks.append(task)
        camera.tasks.append(task)
        db.session.commit()
    except exc.SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            return jsonify({ 'message': error, }), 400
    else:
        return jsonify({
        'message': 'Tarea editada con éxito',
    })


def delete(id):
    task = db.session.query(Task).get(id)

    if task is not None:
        try:
            db.session.delete(task)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'message': 'Something was wrong!'}), 400
        else:
            return jsonify({'message': 'task deleted succesfully'})
    else:
        return jsonify({'message': 'The task not exist'}), 400

def turn_off(id):
    task = db.session.query(Task).get(id)
    task.status = '0'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Tarea desactivada'})

def getTimeInterval(time):
    if time == '0':
        return '00:00', '23:59'

    elif time == '1':
        return '07:00', '18:00'

    elif time == '2':
        return '18:00', '07:00'
