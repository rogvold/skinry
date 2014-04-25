import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, abort, jsonify, make_response
from werkzeug import secure_filename
import uuid, base64
import skinscan
from werkzeug.contrib.fixers import ProxyFix
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg']) #JPG ONLY?
SQLALCHEMY_DATABASE_URI = "postgresql://skinry_user:skinry1A@localhost/skinry_db"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.String, primary_key = True)
    p_name = db.Column(db.String(128), index = True, unique = True)
    pts = db.Column(db.Integer)
    date = db.Column(db.DateTime)

    def __init__(self, id, p_name, pts):
        self.id = id
        self.p_name = p_name
        self.pts = pts
        self.date = datetime.utcnow()

db.create_all()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filename, pts = skinscan.detect_deffects(filename)
            return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
    return render_template('index.html')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)


@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify( { 'error': str(error) } ), 500)

images_db = [] #TODO

def generate_id():
    filename = str(uuid.uuid4())
    while os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename + '.jpg')):
        filename = str(uuid.uuid4())
    return filename 

@app.route("/api/v1/", methods=['POST'])
def api_v1_upload_pic():
    if not request.json or not 'img' in request.json:
        abort(400)
    img_base64 = request.json['img']
    img_id = generate_id()
    f = open(os.path.join(app.config['UPLOAD_FOLDER'], img_id + '.jpg'), "wb")
    f.write(base64.decodestring(img_base64))
    f.close()
    filename, pts = skinscan.detect_deffects(img_id + '.jpg')
    entry = Entry(img_id, filename, pts)
    db.session.add(entry)
    db.session.commit()
    image = {
        'p_name' : filename,
        's_name' : img_id + '.jpg',
        'pts' : pts
    }
    #images_db.append(image)
    return jsonify({'p_name': image['p_name'], 's_name': image['s_name']}), 201

@app.route("/api/v1/source/<filename>", methods=['GET'])
def api_v1_download_source_pic(filename):
    img = Entry.query.get(filename[:-len('.jpg')])#filter(lambda t: t['s_name'] == filename, images_db)
    if img is None:
        abort(404)
    f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "rb") 
    img_base64 = base64.b64encode(f.read())
    f.close()
    return jsonify({'img': img_base64})

@app.route("/api/v1/proc/<filename>", methods=['GET'])
def api_v1_download_proc_pic(filename):
    img = Entry.query.filter_by(p_name=filename).first()
    #img = filter(lambda t: t['p_name'] == filename, images_db)
    if img is None:
        abort(404)
    f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "rb") 
    img_base64 = base64.b64encode(f.read())
    f.close()
    return jsonify({'img': img_base64, 'pts': img.pts})
      

@app.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
    
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
