import requests
import os

url = 'https://cssminifier.com/raw'


def minify():
    css_files = [
        'main.css',
        'cards.css'
    ]
    for css_file in css_files:
        print('Minifying: {}'.format(css_file))
        css = ''
        try:
            path = os.path.join(os.getcwd(), 'static', css_file)
            with open(path, 'r') as file:
                css = file.read()
        except Exception as e:
            print('CSS file with name: {} could not be read: {}'.format(css_file, e))
        payload = {'input': css}
        r = requests.post(url, payload)
        mini_css_path = os.path.join(os.getcwd(), 'static', css_file.replace('.css', '.min.css'))
        with open(mini_css_path, 'w') as m:
            m.write(r.text)
        print('Successfully minified file: {}'.format(css_file))

if __name__ == '__main__':
    minify()