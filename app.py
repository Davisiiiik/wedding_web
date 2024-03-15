from flask import Flask, render_template, request
from gifts import Gifts
import yaml

CONFIG_FILE = "static/yaml/config.yml"
IP = '10.0.0.116'
PORT = 2000

class WebApp(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.menu = [
            {'title': 'Úvod',           'url': 'home'},
            {'title': 'Informace',      'url': 'info'},
            {'title': 'Dotazník',       'url': 'form'},
            {'title': 'Svatební dary',  'url': 'gifts'}
        ]

        self.GiftList = Gifts()

        self.create_pages()

    def create_pages(self):
        @self.route('/')
        def index():
            return render_template('index.html', menu=self.menu, gifts=self.GiftList.get())

        @self.route('/<section>')
        def load_section(section):
            print("Section:", section)
            return render_template(f'{section}.html')

        @self.route('/get_info', methods=['POST'])
        def get_info():
            name = request.form['name']
            return [self.GiftList[name].title, self.GiftList[name].generate_code(name)]

        @self.route('/claim', methods=['POST'])
        def claim():
            name = request.form['name']

            # Mark gift as claimed
            self.GiftList.claim(name)

            return "success"

        @self.route('/free', methods=['POST'])
        def free():
            name = request.form['name']
            code = request.form['code']

            if not code:
                return "error"

            code.upper()

            print("DEBUG:", name, code, self.GiftList[name].free_code)

            if code == self.GiftList[name].free_code:
                # Mark gift as freed
                self.GiftList.free(name)
                return "success"
            else:
                return "error"
            

def get_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config = yaml.load(file, Loader=yaml.Loader)

    return config


def main() -> None:
    config = get_config()
    App = WebApp()

    try:
        App.run(**config)
    except TypeError as err:
        raise Exception("Syntax Error in " + CONFIG_FILE + " file.\n", err)

if __name__ == '__main__':
    main()
