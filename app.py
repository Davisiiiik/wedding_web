from flask import Flask, render_template, request
from gifts import Gifts
from flask_mysqldb import MySQL
import yaml

CONFIG_FILE = "static/yaml/config.yml"
CONFIG_FILE_DEFAULT = "static/yaml/config.default.yml"

class WebApp(Flask):
    def __init__(self, mysql_cfg:dict):
        super().__init__(__name__)
        self.menu = [
            {'title': 'Úvod',           'url': 'home'},
            {'title': 'Informace',      'url': 'info'},
            {'title': 'Dotazník',       'url': 'form'},
            {'title': 'Svatební dary',  'url': 'gifts'}
        ]

        # Config MySQL
        self.config['MYSQL_HOST'] = mysql_cfg.get('hostname')
        self.config['MYSQL_USER'] = mysql_cfg.get('username')
        self.config['MYSQL_PASSWORD'] = mysql_cfg.get('password')
        self.config['MYSQL_DB'] = mysql_cfg.get('database')
        self.Mysql = MySQL(self)
        
        with self.app_context():
            self.GiftList = Gifts(self.Mysql)

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

            if code == self.GiftList[name].free_code:
                # Mark gift as freed
                self.GiftList.free(name)
                return "success"
            else:
                return "error"
            

def get_config() -> dict:
    try:
        # Try to fetch connection and mysql data from config file
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            config:dict = yaml.load(file, Loader=yaml.Loader)

        connection_cfg = config["connection"]
        mysql_cfg = config["mysql"]
    except (FileNotFoundError, KeyError):
        # If file not foud or corrupted, create new from default
        with open(CONFIG_FILE_DEFAULT, "r", encoding="utf-8") as default_file: 
            config:dict = yaml.load(default_file, Loader=yaml.Loader)
        
        # Create new config file and store there default values
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            yaml.dump(config, file, Dumper=yaml.Dumper, sort_keys=False)

        connection_cfg = config.get("connection")
        mysql_cfg = config.get("mysql")

    return connection_cfg, mysql_cfg


def main() -> None:
    connection_cfg, mysql_cfg = get_config()
    App = WebApp(mysql_cfg)

    try:
        App.run(**connection_cfg)
    except TypeError as err:
        raise Exception("Syntax Error in " + CONFIG_FILE + " file.\n", err)

if __name__ == '__main__':
    main()
