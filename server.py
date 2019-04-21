from flask import Flask, Response, request, send_from_directory
import re
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

bad_regex = re.compile("^http(s|)://(www.|)github.com/(.*?/.*?)/blob/(.*)$", re.IGNORECASE)
def handle_non_raw_code_urls(code_url):
    """Some people will give us links to the non raw view"""
    match = bad_regex.match(code_url)
    if match is None:
        return code_url
    else:
        return "https://raw.githubusercontent.com/{0}/{1}".format(
            match.group(3), match.group(4))

gh_raw_re = re.compile("^https://raw.githubusercontent.com/(.*?)/(.*?)/.*/(.*?)$")
file_domain_re = re.compile("^https://(.*?)/.*/(.*?)$")
def extract_dress_name(code_url):
    """Try and turn a URL into a dress name"""
    match = gh_raw_re.match(code_url)
    if match is None:
        match = file_domain_re.match(code_url)
        if match is None:
            return re.sub("^.*//.*/", " ", code_url)
        else:
            return match.group(1) + "'s " + match.group(2) + " glitch code dress"
    else:
        return match.group(1) + " " + match.group(2) + "'s " + match.group(3) + " glitch code dress" 
    

@app.route('/generate_dress', methods=["POST"])
def generate_dress():
    if request.form["url"] is None or len(request.form["url"]) == 0:
        return send_from_directory("static", "missing_url.html")
    else:
        requested_code_url = request.form["url"]
        code_url = handle_non_raw_code_urls(requested_code_url)
        dress_name = extract_dress_name(code_url)
        rows = []
        return Response(
            stream_template('generated.html',
                            dress_name=dress_name,
                            code_url=code_url,
                            rows=rows))

