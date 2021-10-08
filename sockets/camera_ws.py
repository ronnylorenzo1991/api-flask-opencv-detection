from models.Task import *
from models.Weight import *
from config import BASE_DIR, UPLOAD_CFG_FOLDER, UPLOAD_WEIGHTS_FOLDER
from flask import jsonify
import cv2 as cv
import base64
import time
import random
import string
from sqlalchemy.sql.expression import text
from datetime import datetime
from sqlalchemy import exc, func
from models.Camera import *
from models.Event import *
from flask_socketio import SocketIO, emit
import json

socketio = SocketIO(cors_allowed_origins="*")


@socketio.on('ping')
def pongResponse():
    emit('pong')


@socketio.on('enable_camera_detection')
def enable_camera_detection(id):
    camera = db.session.query(Camera).get(id)
    camera.activated = True
    db.session.commit()
    emit(f"detection_{id}")


@socketio.on('enable_task_detection')
def enable_task_detection(id):
    Conf_threshold = 0.6
    NMS_threshold = 0.4
    COLORS = [(0, 255, 0), (0, 0, 255), (255, 0, 0),
              (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    task = db.session.query(Task).get(id)

    class_name = json.loads(task.weight.classes)

    cfg_file = UPLOAD_CFG_FOLDER + task.weight.filename + '.cfg'
    weight_file = UPLOAD_WEIGHTS_FOLDER + task.weight.filename + '.weight'

    net = cv.dnn.readNet(weight_file, cfg_file)
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA_FP16)

    model = cv.dnn_DetectionModel(net)
    model.setInputParams(size=(416, 416), scale=1 / 255, swapRB=True)
    if can_run_job(task) and is_camera_activated(task.camera.id):
        print(f'Iniciando detección para {task.camera.name}')
        capture = cv.VideoCapture(task.camera.url)  # task.camera.url
        task.status = "2"
        db.session.commit()

        starting_time = time.time()
        frame_counter = 0
        success, image_capture = capture.read()
        if not success:
            print('No hay conexión con el recurso solicitado')
            task.status = "0"
            update_camera_status(task.camera.id)
            emit(f"connection_failed_{id}", {
                'message': "No hay conexión con el recurso solicitado",
            })
            db.session.commit()
        while True:
            if not is_task_running(task.id):
                print('El proceso ha sido detenido')
                break
            if not capture.isOpened():
                continue

            success, image_capture = capture.read()
            frame_counter += 1
            if not success:
                time.sleep(50)
                continue

            classes, scores, boxes = model.detect(
                image_capture, Conf_threshold, NMS_threshold)

            image_name = ''.join(random.choices(
                string.ascii_letters + string.digits, k=20))


            for (class_id, score, box) in zip(classes, scores, boxes):
                # save clean image
                cv.imwrite(BASE_DIR + f'/resources/images/event_detection/{image_name}.clean.png', image_capture)
                color = COLORS[int(class_id) % len(COLORS)]
                label = "%s : %f" % (
                    class_name[class_id[0]], (score * 100).round())

                cv.rectangle(image_capture, box, color, 1)
                cv.putText(image_capture, label, (box[0], box[1] - 10),
                           cv.FONT_HERSHEY_COMPLEX, 0.3, color, 1)

                cv.imwrite(BASE_DIR + f'/resources/images/event_detection/{image_name}.png', image_capture)

                save_event(task, class_name[class_id[0]], score * 100, image_name, box)
                emit(f"event_generated", broadcast=True)

            ending_time = time.time() - starting_time
            fps = frame_counter / ending_time

            # write camera name and FPS
            cv.putText(image_capture, f'{task.camera.name} FPS: {fps}', (20, 50),
                       cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

            image_capture = cv.imencode('.jpg', image_capture)[1].tobytes()
            image_capture = base64.b64encode(image_capture).decode('utf-8')
            emit(f"detection_{task.id}", {
                'image': "data:image/jpeg;base64,{}".format(image_capture),
            }, broadcast=True)
            emit(f"detection_init_{id}", broadcast=True)
            db.session.remove()
    print('proceso detenido')
    emit(f"connection_failed_{id}", {
        'message': "No se puede procesar esta tarea. Revise que la fuente este habilitada",
    })


def save_event(task, labels, score, image_name, box):
    last_event = Event.query.order_by(text('id desc')).first()
    e_number = get_next_number(last_event)
    e_description = f"Evento detectado en {task.camera.name}"
    e_score = round(score[0])
    e_image = image_name
    e_classes = labels
    e_coordinates = box.tolist()
    e_date = datetime.now()
    current_camera = Camera.query.get(task.camera_id)
    current_weight = Weight.query.get(task.weight_id)
    event = Event(
        description=e_description,
        number=e_number,
        score=e_score,
        image=e_image,
        classes=e_classes,
        coordinates=e_coordinates,
        date=e_date,
    )

    try:
        db.session.add(event)
        current_camera.events.append(event)
        current_weight.events.append(event)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        error = str(e.__dict__['orig'])

        return jsonify({'message': error, }), 400
    else:
        return jsonify({
            'message': 'Event created succesfully',
        })


def is_camera_activated(id):
    camera = db.session.query(Camera).get(id)
    return camera.activated


def get_next_number(event):
    if not event:
        return 1
    else:
        return event.number + 1


def can_run_job(task):
    return (task.status == "0" or task.status == "1") and is_in_time(task.start, task.end)


def is_in_time(start, end):
    now = datetime.now().time()

    return now >= start and now <= end


def update_camera_status(id):
    camera = db.session.query(Camera).get(id)
    camera.activated = False
    is_run = False
    for task in camera.tasks:
        if task.status == '2':
            is_run = True
    if is_run:
        camera.activated = True
    db.session.commit()


def is_task_running(id):
    task = db.session.query(Task).get(id)
    return task.status == "2"
