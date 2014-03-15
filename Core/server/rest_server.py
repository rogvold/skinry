import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, abort, jsonify
from werkzeug import secure_filename
import uuid, base64

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif']) #JPG ONLY?

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
    return render_template('index.html')


##TODO: Error handler

images_db = [] # DB?

def generate_id():
    return str(uuid.uuid4()) #TODO: CHECK

@app.route("/api/v1/", methods=['POST'])
def api_v1_upload_pic():
    if not request.json or not 'img' in request.json:
        abort(400)
    img_base64 = request.json['img']
    img_id = generate_id()
    f = open(os.path.join(app.config['UPLOAD_FOLDER'], img_id + '.jpg'), "wb")
    f.write(base64.decodestring(img_base64))
    f.close()
    # IMAGE PROCESSING HERE
    # SAVING /uploads/<id> 
    processed_img_base64 = img_base64
    image = {
        'id' : img_id,
        'img' : processed_img_base64
    }
    images_db.append(image)
    return jsonify({'id': image['id']}), 201

@app.route("/api/v1/<filename>", methods=['GET'])
def api_v1_download_pic(filename):
    f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename + '.jpg'), "rb") #TODO: check filename?
    img_base64 = base64.b64encode(f.read())
    f.close()
    return jsonify({'img': img_base64})
      

@app.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
