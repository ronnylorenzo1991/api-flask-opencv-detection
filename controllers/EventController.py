from operator import and_
from config import BASE_DIR
from sqlalchemy.sql.expression import text
from models.Event import Event, events_schema
from flask import request, jsonify, send_file, json
from sqlalchemy import exc, and_, func, or_
import datetime
import calendar
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def get_all():
    startDate = ''
    endDate = ''
    cameras = []
    weights = []
    cameraConds = []
    weightsConds = []
   
    if request.args.get('startDate'):
        startDate = datetime.datetime.strptime(request.args.get('startDate'), "%m/%d/%Y")
    if request.args.get('endDate'):
        endDate = datetime.datetime.strptime(request.args.get('endDate') + ' 23:59:59', "%m/%d/%Y %H:%M:%S")
    if request.args.get('cameras'):
        cameras = request.args.get('cameras').split(",")
        for camera in cameras:
            cameraConds.append(Event.camera_id == camera)
    if request.args.get('weights'):
        weights = request.args.get('weights').split(",")    
        for weight in weights:
            weightsConds.append(Event.weight_id == weight)
    
    sort = request.args.get('sort').split("|")
    sort_dir = text(sort[0] + " " + sort[1]) if sort[0] else text('id desc')
    per_page = int(request.args.get('per_page'))
    page = int(request.args.get('page'))
    events =  db.session.query(Event)
    events = events.filter(and_(Event.date >= startDate, Event.date <= endDate))
    events = events.filter(or_(*cameraConds))
    events = events.filter(or_(*weightsConds))
    total = events.count()
    events = events.order_by(sort_dir).paginate(int(page), int(per_page), False)
    result = events_schema.dump(events.items)
    offset = (page - 1) * per_page
    item_from = offset + 1
    item_to = offset + per_page
    if not events.has_next:
        item_to = total

    return jsonify({
        "total": total,
        "per_page": per_page,
        "current_page": page,
        "last_page": events.pages,
        "next_page_url": "",
        "prev_page_url": "",
        "from": item_from,
        "to": item_to,
        'data': result
    })


def create():
    last_event = Event.query.order_by(text('id desc')).first()
    e_number = get_next_number(last_event)
    e_description = request.form['description']
    e_score = request.form['score']
    e_source = request.form['source']
    e_image = request.form['image_name']
    date = datetime.now()

    event = Event(
        description=e_description,
        number=e_number,
        score=e_score,
        source=e_source,
        image=e_image,
        date=date,
    )

    try:
        db.session.add(event)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        error = str(e.__dict__['orig'])

        return jsonify({'message': error, }), 400
    else:
        return jsonify({
            'message': 'Event created succesfully',
        })


def delete(id):
    event = db.session.query(Event).get(id)

    if event is not None:
        try:
            db.session.delete(event)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'message': 'Something was wrong!'}), 400
        else:
            return jsonify({'message': 'Event deleted succesfully'})
    else:
        return jsonify({'message': 'The Event not exist'}), 400


def total_by_source():
    source = request.args.get('source')

    events_by_source = Event.query.filter_by(source=source).count()
    return jsonify({
        'source': request.args.get('source'),
        'total': events_by_source
    })


def total_by_month():
    month_labels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    labels = []
    cameras = []
    weights = []
    cameraConds = []
    weightsConds = []
    startYear = int(request.args.get('startDate').rpartition('/')[2])
    endYear = int(request.args.get('endDate').rpartition('/')[2])
    results = []

    if request.args.get('cameras'):
        cameras = request.args.get('cameras').split(",")
        for camera in cameras:
            cameraConds.append(Event.camera_id == camera)

    if request.args.get('weights'):
        weights = request.args.get('weights').split(",") 
        for weight in weights:
            weightsConds.append(Event.weight_id == weight)   

    if startYear == endYear:
        startMonth = int(request.args.get('startDate').partition('/')[0])
        endMonth = int(request.args.get('endDate').partition('/')[0])
       
        while startMonth <= endMonth:
            labels.append(month_labels[startMonth - 1])
            num_days = calendar.monthrange(startYear, startMonth)[1]
            start_date = datetime.date(startYear, startMonth, 1)
            end_date = datetime.date(endYear, startMonth, num_days)
            events = db.session.query(Event).filter(
                and_(Event.date >= start_date, Event.date <= end_date))
            events = events.filter(or_(*cameraConds))
            events = events.filter(or_(*weightsConds))
            results.append(events.count())
            startMonth = startMonth + 1

    else:
        while startYear <= endYear:
            labels.append(startYear)
            start_date = datetime.date(startYear, 1, 1)
            end_date = datetime.date(startYear, 12, 31)
            events = db.session.query(Event).filter(
            and_(Event.date >= start_date, Event.date <= end_date))
            events = events.filter(or_(*cameraConds))
            events = events.filter(or_(*weightsConds))
            results.append(events.count())
            startYear = startYear + 1

    return jsonify({'totals': results, 'labels': labels})


def total_by_score():
    over = request.args.get('over')
    between1 = request.args.get('betwOne')
    between2 = request.args.get('betwTwo')
    under = request.args.get('under')
    results = []

    results.append(db.session.query(Event).filter(
        and_(Event.score >= over)).count())
    results.append(db.session.query(Event).filter(
        and_(Event.score < between1, Event.score > between2)).count())
    results.append(db.session.query(Event).filter(
        and_(Event.score <= under)).count())

    return jsonify({'totals': results})


def totals_by_classes():
    results = []
    events = db.session.query(
        db.func.count(Event.classes),
        Event.classes
    ).group_by(
        Event.classes
    ).having(
        db.func.count(Event.classes) > 1
    )
    results.append(db.session.query(Event).group_by(Event.classes))

    result = events_schema.dump(events)
    labels = {}
    for label in result:
        labels[label['classes']] = []
        year = 2021
        month = 1
        while month <= 12:
            num_days = calendar.monthrange(year, month)[1]
            start_date = datetime.date(year, month, 1)
            end_date = datetime.date(year, month, num_days)

            labels[label['classes']].append(db.session.query(Event).filter(
                and_(Event.date >= start_date, Event.date <= end_date, Event.classes == label['classes'])).count())
            month += 1

    return jsonify({'totals': labels})


def get_all_events():
    events = Event.query.all()
    result = events_schema.dump(events)

    return result


def get_next_number(event):
    if not event:
        return 1
    else:
        return event.number + 1


def get_image(name):
    
    filename = BASE_DIR + f'/resources/images/event_detection/{name}.png'
    print(filename)
    return send_file(filename, mimetype='image/png')
