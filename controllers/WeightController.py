from config import ALLOWED_CFG_EXTENSIONS, ALLOWED_WEIGHTS_EXTENSIONS, BASE_DIR, UPLOAD_CFG_FOLDER, UPLOAD_WEIGHTS_FOLDER
from sqlalchemy.sql.expression import text
from flask import request, jsonify
from sqlalchemy import exc
from models.Weight import *
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

db = SQLAlchemy()


def get_all():
    sort = request.args.get('sort').split("|")
    sort_dir = text(sort[0] + " " + sort[1]) if sort[0] else text('id desc')
    per_page = int(request.args.get('per_page'))
    page = int(request.args.get('page'))
    total = Weight.query.count()
    weights = Weight.query.order_by(sort_dir).paginate(page,per_page,error_out=False)
    result = weights_schema.dump(weights.items)
    offset = (page - 1) * per_page
    item_from = offset + 1
    item_to = offset + per_page
    if not weights.has_next:
        item_to = total
    
    return jsonify({
        "total":total,
        "per_page":per_page,
        "current_page":page,
        "last_page":weights.pages,
        "next_page_url":"",
        "prev_page_url":"",
        "from":item_from ,
        "to":item_to , 
        'data':result
        })

def create():
    w_name = request.form['name']
    w_classes = request.form['classes']
    w_description = request.form['description']
    
    if 'fileWeight' not in request.files or 'fileCfg' not in request.files:
        return jsonify({'message': 'Debe seleccionar los ficheros necesarios'}), 400
   
    # Upload Weight file
    fileWeight = request.files['fileWeight']
    if fileWeight.filename == '':
        return jsonify({'message': 'Se requiere un fichero de modelo'}), 400
    
    if fileWeight and allowed_file_weight(fileWeight.filename):
            fileWeight.save(UPLOAD_WEIGHTS_FOLDER + w_name + '.weight')
    else:
        return jsonify({'message': 'Extension de fichero no permitida'}), 400

    # Upload Config file
    fileCfg = request.files['fileCfg']
    if fileCfg.filename == '':
        return jsonify({'message': 'Se requiere un fichero de configuración'}), 400
    
    if fileCfg and allowed_file_cfg(fileCfg.filename):
            fileCfg.save(UPLOAD_CFG_FOLDER + w_name + '.cfg')
    else:
        return jsonify({'message': 'Format Incorrect'}), 400    

    weight = Weight(
        filename = w_name,
        classes = w_classes,
        description = w_description,
        )

    try:
        db.session.add(weight)
        db.session.commit()
    except exc.SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            return jsonify({ 'message': error, }), 400
    else:
        return jsonify({
        'message': 'Weight created succesfully',
    })

def edit(id):
    weight = db.session.query(Weight).get(id)
    weight.filename = request.form['name']
    weight.description = request.form['description']
    weight.classes = request.form['classes']

    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            return jsonify({ 'message': error, }), 400
    else:
        return jsonify({
        'message': 'Weight edited succesfully',
    })

def delete(id):
    weight = db.session.query(Weight).get(id)
   
    if weight is not None:
        try:
             db.session.delete(weight)
             db.session.commit()
        except exc.SQLAlchemyError as e:
             db.session.rollback()
             return jsonify({ 'message': 'Something was wrong!' }), 400
        else:
            return jsonify({ 'message': 'Weight deleted succesfully' })
    else:
        return jsonify({ 'message': 'The Weight not exist' }), 400

def allowed_file_weight(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_WEIGHTS_EXTENSIONS

def allowed_file_cfg(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_CFG_EXTENSIONS