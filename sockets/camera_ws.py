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
from datetime import datetime, date, timedelta
from sqlalchemy import exc, func
from models.Camera import *
from models.Event import *
from flask_socketio import SocketIO, emit
import json
import numpy as np
import shutil

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
    task = db.session.query(Task).get(id)  # Getting current task

    # Run Detection
    if can_run_job(task) and is_camera_activated(task.camera.id):
        # Set Config values
        cfg_file = UPLOAD_CFG_FOLDER + task.weight.filename + '.cfg'
        weight_file = UPLOAD_WEIGHTS_FOLDER + task.weight.filename + '.weight'
        class_name = task.weight.classes

        conf_threshold = 0.6
        nms_threshold = 0.4
        colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0),
                  (255, 255, 0), (255, 0, 255), (0, 255, 255)]

        net = cv.dnn.readNet(weight_file, cfg_file)
        net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA_FP16)

        model = cv.dnn_DetectionModel(net)
        model.setInputParams(size=(416, 416), scale=1 / 255, swapRB=True)
        starting_time = time.time()
        last_event_time = time.time()
        last_event = event_schema.dump(
            db.session.query(Event.coordinates, Event.classes).order_by(Event.id.desc()).first())
        if last_event != {}:
            last_event_class = last_event['classes']
        else:
            last_event_class = ''

        frame_counter = 0

        print(f'Iniciando detección para {task.camera.name}')
        toggle_activate_task(task.id, "2")  # Update task status to in process

        capture = cv.VideoCapture(task.camera.url)
        success, image_capture = capture.read()
        if not success or not capture.isOpened():
            print('No hay conexión con el recurso solicitado')
            toggle_activate_task(task.id, "0")  # Update task status to stopped
            update_camera_status(task.camera.id)
            emit(f"connection_failed_{id}", {
                'message': "No hay conexión con el recurso solicitado",
            })

        while True:
            if not is_task_running(task.id):
                print('El proceso ha sido detenido')
                break

            success, image_capture = capture.read()
            frame_counter += 1
            if not success:
                time.sleep(10)
                capture = cv.VideoCapture(task.camera.url)
                continue

            try:
                classes, scores, boxes = model.detect(
                    image_capture, conf_threshold, nms_threshold)
            except cv.error as e:
                print(e)
                time.sleep(10)
                capture = cv.VideoCapture(task.camera.url)
                continue

            # save temp clean image
            cv.imwrite(BASE_DIR + f'/resources/images/temp_detection_image/temp.png', image_capture)
            for (class_id, score, box) in zip(classes, scores, boxes):
                color = colors[int(class_id) % len(colors)]
                label = "%s : %f" % (
                    class_name[class_id[0]], (score * 100).round())
                cv.rectangle(image_capture, box, color, 1)
                cv.putText(image_capture, label, (box[0], box[1] - 10),
                           cv.FONT_HERSHEY_COMPLEX, 0.3, color, 1)

                if not is_same_detection_event(box, last_event_time, time.time(),
                                               last_event_class, class_name[class_id[0]]):
                    try:
                        image_name = ''.join(random.choices(
                            string.ascii_letters + string.digits, k=20))
                        # Copy temp image to event detection folder
                        shutil.copy(BASE_DIR + f'/resources/images/temp_detection_image/temp.png',
                                    BASE_DIR + f'/resources/images/event_detection/{image_name}.png')
                        save_event(task, class_name[class_id[0]], score * 100, image_name, box)
                        last_event_time = time.time()
                        last_event_class = class_name[class_id[0]]
                    except:
                        continue

                emit(f"event_generated", broadcast=True)

            ending_time = time.time() - starting_time
            fps = frame_counter / ending_time

            # write camera name and FPS
            cv.putText(image_capture, f'{task.camera.name} FPS: {fps}', (20, 50),
                       cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

            image_capture = cv.imencode('.jpg', image_capture)[1].tobytes()
            image_capture = base64.b64encode(image_capture).decode('utf-8')

            # Streaming detection signal
            emit(f"detection_{task.id}", {
                'image': "data:image/jpeg;base64,{}".format(image_capture),
            }, broadcast=True)
            emit(f"detection_init_{id}", broadcast=True)
            db.session.remove()

    if not is_camera_activated(task.camera.id):
        print('fuente no activa')
        emit(f"connection_failed_{id}", {
            'message': "No se puede procesar esta tarea. Revise que la fuente este habilitada",
        })
    elif task.status == '1':  # Status 1 pending
        print('Tarea Pendiente')
        emit(f"detection_init_{id}")


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
    return (task.status == "0" or task.status == "1") and is_in_time(task)  # Status 0 stopped, 1 pending


def is_in_time(task):
    start = datetime.strptime(f"{date.today()} {task.start}", '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(f"{date.today()} {task.end}", '%Y-%m-%d %H:%M:%S')
    now = datetime.now()

    if task.start > task.end:
        end = end + timedelta(days=1)

    if start <= now <= end:
        return True
    else:
        task.status = '1'  # Status 2 pending
        db.session.commit()
        return False


def update_camera_status(id):
    camera = db.session.query(Camera).get(id)
    camera.activated = False
    is_run = False
    for task in camera.tasks:
        if task.status == '2':  # Status 2 in process
            is_run = True
    if is_run:
        camera.activated = True
    db.session.commit()


def is_task_running(id):
    task = db.session.query(Task).get(id)
    return task.status == "2"  # Status 2 in process


def toggle_activate_task(id, status):
    task = db.session.query(Task).get(id)
    task.status = status
    db.session.commit()


def is_same_detection_event(box, last_time, now_time, last_event_class, event_class):
    diff_time = now_time - last_time
    # difference time less than 2 minutes (120 sec)
    return diff_time < 120 and last_event_class == event_class and exist_in_last_events(box, event_class)


def exist_in_last_events(box, classes):
    exist = False
    margin = 50  # Distance margin between coordinate values
    comp_results1 = []
    comp_results2 = []
    now_date = datetime.now()
    past_date = datetime.now() - timedelta(hours=0, minutes=10)
    if len(box):
        last_ten_events = events_schema.dump(
            db.session.query(Event.coordinates).filter(Event.classes == classes).filter(
                Event.date.between(past_date, now_date)).order_by(Event.id.desc()).limit(10))

        for item in last_ten_events:
            last_box = np.array(item['coordinates'])
            if len(last_box):
                comp_results1 = box >= last_box - margin
                comp_results2 = box <= last_box + margin
                if all(comp_results1) and all(comp_results2):
                    exist = True
                    break
    return exist
