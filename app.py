from flask import Flask, render_template

class WebApp(Flask):
    def __init__(self):
        super().__init__(__name__, template_folder='pages')
        self.menu = [
            {'title': 'Úvod',           'url': 'home'},
            {'title': 'Informace',      'url': 'info'},
            {'title': 'Dotazník',       'url': 'form'},
            {'title': 'Svatební dary',  'url': 'gifts'}
        ]

        self.create_pages()

    def create_pages(self):
        @self.route('/')
        def index():
            return render_template('index.html', menu=self.menu)

        @self.route('/<section>')
        def load_section(section):
            return render_template(f'{section}.html')


def main():
    App = WebApp()
    App.run(debug=True, host='10.0.0.116', port=2000)

if __name__ == '__main__':
    main()
