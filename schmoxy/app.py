import os
from urlparse import urljoin
import base64

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


def get_resource(cache_dir, url):
    """Return a resource (text or binary) from cache or download,
    cache and return"""
    filename = base64.b64encode(url, '+_')
    try:
        with open(os.path.join(cache_dir,filename), 'r') as cached:
            page_content = cached.read()
    except IOError:
        page = requests.get(url)
        if page.headers['content-type'].startswith('text/html'):
            page_content = replace_references(page.text,
                                              app.config['PROXY_ORIGIN'],
                                              urls,
                                              app.config['SERVER_NAME'])
            with open(os.path.join(cache_dir, filename), 'w') as cached:
                cached.write(page_content.encode('utf-8'))
        elif page.headers['content-type'].startswith('image'):
            page_content = page.content
            with open(os.path.join(cache_dir, filename), 'wb') as cached:
                cached.write(page_content)

    return page_content


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if not path:
        return get_resource(app.config['PROXY_ORIGIN'])

    local_path = "http://%s/%s" % (app.config['SERVER_NAME'], path)
    data = get_resource(urls[local_path])
    try:
        resp = requests.get(urljoin(app.config['PROXY_ORIGIN'], ))
    except KeyError:
        abort(404)
    if resp.status_code != 200:
        return ''
    response = make_response(resp.content)
    response.headers['content-length'] = response.headers['content-length']
    response.headers['content-type'] = response.headers['content-type']
    return response
