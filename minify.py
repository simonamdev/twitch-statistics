import requests
import os

css_url = 'https://cssminifier.com/raw'
js_url = 'https://javascript-minifier.com/raw'


def minify_file(file_name='', type='css'):
    print('Minifying: {}'.format(file_name))
    text = ''
    try:
        path = os.path.join(os.getcwd(), 'static', file_name)
        with open(path, 'r') as file:
            text = file.read()
    except Exception as e:
        print('CSS file with name: {} could not be read: {}'.format(file_name, e))
    payload = {'input': text}
    if type == 'css':
        r = requests.post(css_url, payload)
    else:
        r = requests.post(js_url, payload)
    mini_file_path = os.path.join(os.getcwd(), 'static', file_name.replace('.{}'.format(type), '.min.{}'.format(type)))
    with open(mini_file_path, 'w') as m:
        m.write(r.text)
    print('Successfully minified file: {}'.format(file_name))


def minify():
    files = os.listdir('static')
    files.remove('images')  # remove images folder
    files = [file for file in files if not '.min.' in file]  # remove old minified files
    css_files = [file for file in files if file.endswith('.css')]
    js_files = [file for file in files if file.endswith('.js')]
    for css_file in css_files:
        minify_file(css_file, type='css')
    # currently disabled
    """
    for js_file in js_files:
        minify_file(js_file, type='css')
    """

if __name__ == '__main__':
    minify()
