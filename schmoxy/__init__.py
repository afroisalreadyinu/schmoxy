import os
from urlparse import urlparse, urljoin, ParseResult

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for)
import requests
from BeautifulSoup import BeautifulSoup

app = Flask('adana')
app.config.from_pyfile('configs/config.cfg')

def replace_references(page_text, source_url):
    soup = BeautifulSoup(page_text)
    for img in soup.findAll('img'):
        src = urlparse(img['src'])
        import pdb;pdb.set_trace()
        if not src.netloc:
            src = urlparse(urljoin(source_url, img['src']))
        img['src'] = ParseResult(src.scheme,
                                 app.config['SERVER_NAME'],
                                 src.path, src.params, src.query, src.fragment).geturl()
        #img['src'] = 'http://shift.retresco.de/static/img/shift_logo_20x115.png'
    return unicode(soup)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if not path:
        try:
            with open(os.path.join(app.config['CACHE_PATH'],
                                   'index'), 'r') as cached:
                page_content = cached.read()
        except IOError:
            page = requests.get(app.config['PROXY_ORIGIN'])
            page_content = replace_references(page.text, app.config['PROXY_ORIGIN'])
            with open(os.path.join(app.config['CACHE_PATH'],
                                   'index'), 'w') as cached:
                cached.write(page_content.encode('utf-8'))
        return page_content

    print "NEED ", path
    return requests.get(urljoin(app.config['PROXY_ORIGIN'], path)).text


if __name__ == '__main__':
    app.run()
