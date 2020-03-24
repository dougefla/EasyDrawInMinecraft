	# -*- coding: utf-8 -*-
import os
from flask import Flask, request, url_for, send_from_directory,send_file
from werkzeug.utils import secure_filename
import drawinmc as draw

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/var/www/flask-prod/upload/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


html = '''
    <!DOCTYPE html>
    <html>
    <head> 
        <style> 
        body{text-align:center} 
        </style> 
        </head> 
<meta HTTP-EQUIV="pragma" CONTENT="no-cache"> 
<meta HTTP-EQUIV="Cache-Control" CONTENT="no-store, must-revalidate"> 
<meta HTTP-EQUIV="expires" CONTENT="Wed, 26 Feb 1997 08:21:57 GMT"> 
<meta HTTP-EQUIV="expires" CONTENT="0">
<Meta http-equiv="Set-Cookie" Content="cookievalue=xxx; expires=Wednesday,21-Oct-98 16:14:21 GMT; path=/">

    <body>
    <title>Easy Draw in MC</title>
    <h1>Easy Draw in MC</h1>
    <h2>Please Upload Picture</h2>

    <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
    </form>
	<br>
	<script>
		var now = new Date().getTime();
		document.write('<a href="/download?v=' + now + '" rel="stylesheet" type="text/css"/>Download</a>');
	</script>
	</br>
    <br>
        Note: About how to use the 'result.mcfunction', please refer to <a href="https://minecraft-zh.gamepedia.com/%E5%87%BD%E6%95%B0%EF%BC%88Java%E7%89%88%EF%BC%89">here</a>
    </br>

    <br>
        <h3>By @Douge, ZJU</h3>
    </br>
    </body>
    </html>

    '''


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/download', methods=['GET'])
def download():
    if request.method == "GET":
        return send_from_directory('/var/www/flask-prod/', 'result.mcfunction', as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory('/var/www/flask-prod/upload/',filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('/var/www/flask-prod/upload/', filename))
            file_url = url_for('uploaded_file', filename=filename)
            draw.draw(('/var/www/flask-prod/upload/'+filename),128,[10,10,10])
            return html + '<br><img src=' + file_url + '>'
    return html



if __name__ == '__main__':
    app.run()