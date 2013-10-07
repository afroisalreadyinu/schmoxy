import os
from urlparse import urlparse, urljoin, ParseResult

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   make_response)
import requests
from BeautifulSoup import BeautifulSoup

app = Flask('adana')
app.config.from_pyfile('configs/config.cfg')

class BiDict(object):
    def __init__(self):
        self.one = dict()
        self.two = dict()

    def __getitem__(self, key):
        try:
            return self.one[key]
        except KeyError:
            return self.two[key]

    def __setitem__(self, key, value):
        print "MAPPED ", key, " AND ", value
        self.one[key] = value
        self.two[value] = key

urls = BiDict()
parsed_origin = urlparse(app.config['PROXY_ORIGIN'])

def fetch_index():
    try:
        with open(os.path.join(app.config['CACHE_PATH'],
                               'index'), 'r') as cached:
            page_content = cached.read()
    except IOError:
        print "downloading page"
        page = requests.get(app.config['PROXY_ORIGIN'])
        print "page downloaded"
        page_content = replace_references(page.text, app.config['PROXY_ORIGIN'])
        with open(os.path.join(app.config['CACHE_PATH'],
                               'index'), 'w') as cached:
            cached.write(page_content.encode('utf-8'))
    return page_content


def replace_references(page_text, source_url):
    global urls
    soup = BeautifulSoup(page_text)
    for img in soup.findAll('img'):
        src = urlparse(img['src'])
        if not src.netloc:
            #we want the absolut url so that it can be downloaded later
            src = urlparse(urljoin(source_url, img['src']))
        try:
            new_src = urls[src.geturl()]
        except KeyError:
            new_src = ParseResult('http',
                                  app.config['SERVER_NAME'],
                                  src.path, src.params, src.query, src.fragment).geturl()
            urls[src.geturl()] = new_src
        img['src'] = new_src
    return unicode(soup)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if not path:
        return fetch_index()
    real_path = "http://%s/%s" % (app.config['SERVER_NAME'], path)
    resp = requests.get(urljoin(app.config['PROXY_ORIGIN'], urls[real_path]))
    if resp.status_code != 200:
        return ''
    response = make_response(resp.content)
    response.headers['content-length'] = response.headers['content-length']
    response.headers['content-type'] = response.headers['content-type']
    return response


if __name__ == '__main__':
    app.run()
