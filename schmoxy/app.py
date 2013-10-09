import os
from urlparse import urljoin
import base64
import json

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

class ResourceCache(object):

    def __init__(self, cache_dir, origin, server_name):
        self.cache_dir = cache_dir
        self.origin = origin
        self.server_name = server_name

    def format_headers(self, headers):
        dump = json.dumps(dict(headers))
        return "%d%s" % (len(dump), dump)


    def read_file(self, path):
        with open(path, 'r') as cached:
            content = cached.read()
            header_length = content[:7].split('{')[0]
            header_json = content[len(header_length):len(header_length) + int(header_length)]
            headers = json.loads(header_json)
            content = content[len(header_length) + int(header_length):]
        return headers, content

    def get_resource(self, url):
        """Return a resource (text or binary) from cache or download,
        cache and return"""
        filename = base64.b64encode(url, '+_')
        try:
            headers, page_content = self.read_file(os.path.join(self.cache_dir,
                                                                filename))
        except IOError:
            page = requests.get(url)
            if page.headers['content-type'].startswith('text/html'):
                page_content = replace_references(page.text,
                                                  self.origin,
                                                  urls,
                                                  self.server_name)

            elif page.headers['content-type'].startswith('image'):
                page_content = page.content
            with open(os.path.join(self.cache_dir, filename), 'w') as cached:
                cached.write(self.format_headers(page.headers))
                out_content = (page_content.encode('utf-8')
                               if page.headers['content-type'].startswith('text')
                               else page_content)
                cached.write(out_content)
            headers = page.headers

        return headers, page_content

@app.before_request
def before_request():
    g.resource_cache = ResourceCache(app.config['CACHE_PATH'],
                                     app.config['PROXY_ORIGIN'],
                                     app.config['SERVER_NAME'])

TO_BE_COPIED = ['content-length', 'content-type']

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if not path:
        headers, content = g.resource_cache.get_resource(app.config['PROXY_ORIGIN'])
    else:
        local_path = "http://%s/%s" % (app.config['SERVER_NAME'], path)
        headers, content = g.resource_cache.get_resource(urls[local_path])
    response = make_response(content)
    for key in TO_BE_COPIED:
        if key in headers:
            response.headers[key] = headers[key]
    return response
