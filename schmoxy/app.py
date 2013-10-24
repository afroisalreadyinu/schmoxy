import os
from urlparse import urljoin
import base64
import json
import codecs

from flask import (Flask, g,
                   abort,
                   render_template,
                   request,
                   redirect,
                   make_response)
import requests
from schmoxy.util import BiDict
from schmoxy.doc_processor import replace_references

app = Flask('adana', static_url_path='/justdontservethosefilesreally')
app.config.from_pyfile(os.path.abspath(os.path.join(__file__,
                                                    '../configs/config.cfg')))

urls = BiDict()

def is_int(thing):
    try:
        int(thing)
    except ValueError:
        return False
    return True

class SchmoxyRetrieveError(Exception):
    pass

class ResourceCache(object):

    def __init__(self, cache_dir, origin, server_name, excluded_js):
        self.cache_dir = cache_dir
        self.origin = origin
        self.server_name = server_name
        self.excluded_js = excluded_js

    def format_headers(self, headers):
        dump = json.dumps(dict(headers))
        return "%d%s" % (len(dump), dump)


    def read_file(self, path):
        with open(path, 'r') as cached:
            content = cached.read()
            if is_int(content):
                return None, int(content)
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
            if page.status_code > 400:
                with open(os.path.join(self.cache_dir, filename), 'w') as out_file:
                    out_file.write(str(page.status_code))
                return None, page.status_code
            if page.headers['content-type'].startswith('text/html'):
                page_content = replace_references(page.content,
                                                  self.origin,
                                                  urls,
                                                  self.server_name,
                                                  self.excluded_js)
            else:
                page_content = page.content
            filepath = os.path.join(self.cache_dir, filename)
            content_type = page.headers['content-type']
            if (content_type.startswith('text') or
                content_type in ['application/javascript']):
                if not isinstance(page_content, unicode):
                    page_content = unicode(page_content, 'utf-8', 'ignore')
                cached = codecs.open(filepath, 'w', encoding='utf-8')
                page.headers['content-length'] = len(page_content)
            else:
                cached = open(filepath, 'wb')
            cached.write(self.format_headers(page.headers))
            cached.write(page_content)
            cached.close()
            headers = page.headers
        return headers, page_content


@app.before_request
def before_request():
    g.resource_cache = ResourceCache(app.config['CACHE_PATH'],
                                     app.config['PROXY_ORIGIN'],
                                     app.config['SERVER_NAME'],
                                     app.config['EXCLUDE_JS'])

TO_BE_COPIED = ['content-length', 'content-type']

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if not path:
        headers, content = g.resource_cache.get_resource(app.config['PROXY_ORIGIN'])
    else:
        local_path = "http://%s/%s" % (app.config['SERVER_NAME'], path)
        try:
            headers, content = g.resource_cache.get_resource(urls[local_path])
        except KeyError:
            url = urljoin(app.config['PROXY_ORIGIN'], path)
            headers, content = g.resource_cache.get_resource(url)
            urls[local_path] = url
    if not headers and is_int(content):
        abort(content)
    response = make_response(content)
    for key in TO_BE_COPIED:
        if key in headers:
            response.headers[key] = headers[key]
    return response
