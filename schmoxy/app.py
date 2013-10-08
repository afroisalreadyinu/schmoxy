import os
from urlparse import urljoin
from flask import (Flask, g,
                   abort,
                   render_template,
                   request,
                   redirect,
                   make_response)
import requests
from schmoxy.util import BiDict
from schmoxy.doc_processor import replace_references

app = Flask('adana')
app.config.from_pyfile(os.path.abspath(os.path.join(__file__,
                                                    '../configs/config.cfg')))
urls = BiDict()

def fetch_index():
    try:
        with open(os.path.join(app.config['CACHE_PATH'],
                               'index'), 'r') as cached:
            page_content = cached.read()
    except IOError:
        page = requests.get(app.config['PROXY_ORIGIN'])
        page_content = replace_references(page.text,
                                          app.config['PROXY_ORIGIN'],
                                          urls,
                                          app.config['SERVER_NAME'])
        with open(os.path.join(app.config['CACHE_PATH'],
                               'index'), 'w') as cached:
            cached.write(page_content.encode('utf-8'))
    return page_content


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if not path:
        return fetch_index()

    real_path = "http://%s/%s" % (app.config['SERVER_NAME'], path)
    try:
        resp = requests.get(urljoin(app.config['PROXY_ORIGIN'], urls[real_path]))
    except KeyError:
        abort(404)
    if resp.status_code != 200:
        return ''
    response = make_response(resp.content)
    response.headers['content-length'] = response.headers['content-length']
    response.headers['content-type'] = response.headers['content-type']
    return response
