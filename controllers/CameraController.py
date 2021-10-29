from models.Weight import Weight
from sqlalchemy.sql.expression import text
from flask import Response, request, jsonify
import cv2 as cv
import distutils.util
from sqlalchemy import exc
from datetime import datetime
from models.Camera import *
from models.Task import *
from models.Weight import *
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_all():
    sort = request.args.get('sort').split("|")
    sort_dir = text(sort[0] + " " + sort[1]) if sort[0] else text('id desc')
    per_page = int(request.args.get('per_page'))
    page = int(request.args.get('page'))
    total = Camera.query.count()
    cameras = Camera.query.order_by(sort_dir).paginate(page,per_page,error_out=False)
    result = cameras_schema.dump(cameras.items)
    for camera in result:
        for task in camera['tasks']:
            weight_data = Weight.query.get(task['weight_id'])
            results = weight_schema.dump(weight_data)
            task['weight'] = results

    offset = (page - 1) * per_page
    item_from = offset + 1
    item_to = offset + per_page
    if not cameras.has_next:
        item_to = total
    
    return jsonify({
        "total":total,
        "per_page":per_page,
        "current_page":page,
        "last_page":cameras.pages,
        "next_page_url":"",
        "prev_page_url":"",
        "from":item_from ,
        "to":item_to , 
        'data':result
        })

def get(id):
    camera = db.session.query(Camera).get(id)
    result = camera_schema.dump(camera)

    return jsonify({'camera': result})
    
def create():
    c_name = request.form['name']
    c_url = request.form['url']
    c_activate = distutils.util.strtobool(request.form['activated'])

    camera = Camera(
        name = c_name,
        url = c_url,
        activated = c_activate
        )

    try:
        db.session.add(camera)
        db.session.commit()
    except exc.SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            return jsonify({ 'message': error, }), 400
    else:
        return jsonify({
        'message': 'Camera created succesfully',
    })

def edit(id):
    camera = db.session.query(Camera).get(id)
    camera.name = request.form['name']
    camera.url = request.form['url']
    camera.activated = distutils.util.strtobool(request.form['activated'])

    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            return jsonify({ 'message': error, }), 400
    else:
        return jsonify({
        'message': 'Camera edited succesfully',
    })

def delete(id):
    camera = db.session.query(Camera).get(id)
   
    if camera is not None:
        try:
             db.session.delete(camera)
             db.session.commit()
        except exc.SQLAlchemyError as e:
             db.session.rollback()
             return jsonify({ 'message': 'Something was wrong!' }), 400
        else:
            return jsonify({ 'message': 'Camera deleted succesfully' })
    else:
        return jsonify({ 'message': 'The camera not exist' }), 400

def show(id):
    camera = Camera.query.get(id)
    return Response(get_camera_signal(camera.url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def turn_off(id):
    camera = db.session.query(Camera).get(id)
    camera.activated = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'The Camera was deactivated'})

def get_camera_signal(url):  # only show camera
    camera = cv.VideoCapture(url)

    while True:
        ret_val, image_capture = camera.read()
        if ret_val == False:
            break
        image_capture = cv.imencode('.jpg', image_capture)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + image_capture + b'\r\n')

def it_is_daytime(date):
    time = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    if time.hour>=7 and time.hour<18: 
        return True
    else: 
        return False
        
def get_next_number(event):

    if not event:
        return 1
    else:
        return event.number + 1

def is_camera_activated(id):
    camera = Camera.query.get(id)
    return camera.activated

def getTimeInterval(time): 
    if time == '0':
        return '00:00', '23:59'

    elif time == '1':
        return '07:00', '18:00'

    elif time == '2':
        return '18:00', '07:00'