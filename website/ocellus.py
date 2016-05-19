from flask import Flask, render_template
from minify import minify as minify_css
app = Flask(__name__)

debug_mode = True


@app.route('/')
def index():
    return render_template('index.html', app_version='Alpha 0.1', debug_mode=debug_mode)

if __name__ == '__main__':
    if not debug_mode:
        minify_css()
    app.run(host='127.0.0.1', port=9000, debug=debug_mode)
    # app.run(host='0.0.0.0', port=9000, debug=debug_mode)
