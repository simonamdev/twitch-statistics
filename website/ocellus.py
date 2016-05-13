from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', app_version='Alpha 0.1')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9000, debug=True)
    app.run(host='0.0.0.0', port=9000, debug=False)
