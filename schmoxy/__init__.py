import os

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for)
import requests

app = Flask('adana')
app.config.from_pyfile('configs/config.cfg')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if not path:
        #app.config['CACHE_PATH']
        page = requests.get(app.config['PROXY_ORIGIN'])
        return page.text

if __name__ == '__main__':
    app.run()
