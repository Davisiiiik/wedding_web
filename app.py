from flask import Flask, render_template

class WebApp(Flask):
    def __init__(self):
        super().__init__(__name__, template_folder='pages')
        self.menu = [
            {'title': 'Hlavní stránka', 'url': '/'},
            {'title': 'Místo',          'url': '/place'},
            {'title': 'Dotazník',       'url': '/form'},
            {'title': 'Svatební dary',  'url': '/gifts'}
        ]

        self.create_pages()

    def create_pages(self):
        @self.route('/')
        def index():
            return render_template('index.html', menu=self.menu)

        @self.route('/place')
        def place():
            return render_template('place.html', menu=self.menu)

        @self.route('/form')
        def form():
            return render_template('form.html', menu=self.menu)

        @self.route('/gifts')
        def gifts():
            return render_template('gifts.html', menu=self.menu)


def main():
    App = WebApp()
    App.run(debug=True, host='localhost', port=19000)

if __name__ == '__main__':
    main()
