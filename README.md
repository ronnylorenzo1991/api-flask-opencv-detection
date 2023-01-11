# Api Flask for Computer Vision With MVC Arquitecture and SocketIO for Streaming

Integration with Flask-Cors,Flask-SQLalchemy,and OpenCV extensions.

### Before install requirements
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

### Extension:
- SQL ORM: [Flask-SQLalchemy](http://flask-sqlalchemy.pocoo.org/2.1/)

- SocketIO: [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)

- OpenCV: [OpenCV-Python](https://pypi.org/project/opencv-python/)

## Installation

Install with pip:

```
$ pip install -r requirements.txt
```

## Flask Application Structure 
```
.
|──────app/
| |────controllers/
| | |────CameraController.py
| | |────DefaultController.py
| | |────EventController.py
| | |────TaskController.py
| | |────WeightController.py
| |────migrations/ (after flask migrate command run)
| |────models/
| | |────Camera.py
| | |────Event.py
| | |────Task.py
| | |────Weight.py
| |────resources/
| | |────config/
| | |────images/
| | |────weights/
| |────routes/
| | |────camera_bp.py
| | |────default_bp.py
| | |────event_bp.py
| | |────task_bp.py
| | |────weight_bp.py
| |────sockets/
| | |────camera_ws.py
|──────app.py
|──────config.py

```


## Getting Started
### Run migration config
```
$ python flask migrate
```
```
$ python flask upgrade
```

### Run api
```
$ python app.py
```

## Changelog
- Version 1.0 : basic Api Flask for Computer Vision With MVC Arquitecture and SocketIO for Streaming
