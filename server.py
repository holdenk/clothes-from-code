from flask import Flask, Response, request, send_from_directory
app = Flask(__name__)

@app.route('/')
def hello_world():
    return send_from_directory("static", "index.html")

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/imgs/<path:path>')
def send_imgs(path):
    return send_from_directory('static/imgs', path)

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


@app.route('/generate_dress', methods=["POST"])
def generate_dress():
    if request.form["url"] is None:
        return send_from_directory("static", "missing_url.html")
    else:
        code_url = request.form["url"]
        return Response(stream_template('generated.html', rows=rows))

