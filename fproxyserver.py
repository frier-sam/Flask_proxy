from flask import Flask, request, abort,flash, redirect, url_for
import hashlib
import json
import requests
import os
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
app = Flask(__name__)

#app.config['CAPTURE'] = bool(os.environ.get('CAPTURE'))
#app.config['CACHE_DIR'] = os.environ.get('CACHE_DIR', '/tmp/cache')

@app.route('/', defaults={'path': ''},methods=['POST','GET'])
@app.route('/<path:path>',methods = ['POST','GET'])
@cross_origin()
#@app.route("/")
def hello(path):
    urldata = path.split('/',1)
    if urldata[0] == 'file':
        return route_file(urldata[1])
    url = 'http://localhost' + ':' + urldata[0]
    if len(urldata)==2:
        url = url +'/'+urldata[1]
    if request.method == 'GET':
        print('getrequest')
        incparms = request.args
        return _retrieve(url,incparms)
    if request.method == 'POST':
        print('postrequest')
        incparms = request.data
        print(incparms)
        return _retrieve(url,incparms)
#     if request.method == 'POST':
#         incparms = request.form
#         return _retrieve(url,incparms)
#      if not url or url.startswith('http://localhost'):
#          return abort(400)
    print('normalrequest')
    return _retrieve(url)


def _retrivepost():
    kwargs = __adapt_request_args(url)
    return response.text,response.status_code, __process_response_headers(response)

def _retrieve(url,incparms=[]):
    response = _request(url,incparms)
    return response.text,response.status_code, __process_response_headers(response)
#    path = _cache_path(url)

#    if not os.path.exists(path):
#        if app.config['CAPTURE']:
#            response = _request(url)
#           _store(url, response)
#        else:
#            return abort(404)

#    with open(path, 'r') as f:
#        cached = json.loads(f.read())
#    return cached['body'], cached['status'], cached['headers']


def _request(url,incparms=[]):
    kwargs = __adapt_request_args(url)
    if len(incparms)==0:
        r = requests.request(request.method, url, **kwargs)
        return r
    r = requests.request(request.method, url,params=incparms, **kwargs)
    return r


def __adapt_request_args(url):
    kwargs = {
        'data': request.data,
        'allow_redirects': False
    }
    headers = dict([(key.upper(), value)
                    for key, value in request.headers.items()])

    # Explicitly set content-length request header
    if 'CONTENT-LENGTH' not in headers or not headers['CONTENT-LENGTH']:
        headers['CONTENT-LENGTH'] = str(len(kwargs['data']))

    # Let requests reset the host for us.
    if 'HOST' in headers:
        del headers['HOST']
    kwargs['headers'] = headers
#     print(kwargs)
    return kwargs


def _store(url, response):
    cached = json.dumps({
        'body': response.text,
        'headers': __process_response_headers(response),
        'status': response.status_code
    })

    path = _cache_path(url)
    dir_ = path.rsplit('/', 1)[0]
    if not os.path.isdir(dir_):
        os.makedirs(dir_)
    with open(path, 'w') as w:
        w.write(cached)


def __process_response_headers(response):
    headers = dict(response.headers)
    headers['content-type'] = 'text/html; charset=utf-8'
    if 'content-encoding' in headers:
        del headers['content-encoding']
    if 'transfer-encoding' in headers:
        del headers['transfer-encoding']
    return headers


def _cache_path(url):
    to_hash = "%s%s%s" % (request.method, url, request.data)
    hashed = hashlib.md5(to_hash).hexdigest()
    address = (hashed[:2], hashed[2:4], hashed)
    return '%s/%s/%s/%s.json' % (app.config['CACHE_DIR'], address)





@app.route('/file', defaults={'path': ''},methods=['POST','GET'])
def route_file(path):
    urldata = path.split('/',1)
    url = 'http://localhost' + ':' + urldata[0]
    if len(urldata)==2:
        url = url +'/'+urldata[1]
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
#         print(request.files)
        fp = request.files['file']
#         kwargs = __adapt_request_args(url)
#         print('filename- {},stream-{},contyoe-{},headers-{}'.format(fp.filename, fp.stream,fp.content_type, fp.headers))
        response = requests.post(url, files={'file':
                                   (fp.filename, fp.stream,
                                    fp.content_type, fp.headers)},data=request.data)
        return response
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
#uploadfile
UPLOAD_FOLDER = '/var/www/html/frontends'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','html','htm','php'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'uploaded successfully'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == "__main__":
    app.run(host='0.0.0.0',port='1111',debug=True)
