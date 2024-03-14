from flask import Flask, render_template, request
from gifts import Gifts

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
            return [self.GiftList[name].title, f"{self.GiftList[name].free_code:X}"]

        @self.route('/claim', methods=['POST'])
        def claim():
            name = request.form['name']

            # Mark gift as claimed
            self.GiftList.claim(name)

            return []

        @self.route('/free', methods=['POST'])
        def free():
            name = request.form['name']
            code = request.form['code']

            if not code:
                return "error"

            code.upper()

            print("DEBUG:", name, code, f"{self.GiftList[name].free_code:X}")

            if code == f"{self.GiftList[name].free_code:X}":
                # Mark gift as freed
                self.GiftList.free(name)
                return "success"
            else:
                return "error"


def main():
    App = WebApp()
    App.run(debug=True, host=IP, port=PORT)

if __name__ == '__main__':
    main()
