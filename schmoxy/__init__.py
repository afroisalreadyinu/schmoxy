from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for)

app = Flask('adana')
app.config.from_pyfile('configs/config.cfg')

@app.route("/")
def index():
    return render_template('index.html')

def run():
    app.run()
