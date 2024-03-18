from flask import Flask, render_template, request
from gifts import Gifts, generate_code
from flask_mysqldb import MySQL
import shutil
import yaml

CONFIG_FILE = "static/yaml/config.yml"
CONFIG_FILE_DEFAULT = "static/yaml/config.default.yml"

class WebApp(Flask):
    def __init__(self, mysql_cfg:dict):
        super().__init__(__name__)
        # Prepare list with dictionaries for every web section
        self.menu = [
            {'title': 'Úvod',           'url': 'home'},
            {'title': 'Informace',      'url': 'info'},
            {'title': 'Dotazník',       'url': 'form'},
            {'title': 'Svatební dary',  'url': 'gifts'}
        ]

        # Check if user set up the connection port
        host:list = mysql_cfg.get('hostname').split(":")
        if len(host) > 1:
            self.config['MYSQL_PORT'] = int(host[1])

        # Configure remaining MySQL connection parameters
        self.config['MYSQL_HOST'] = host[0]
        self.config['MYSQL_USER'] = mysql_cfg.get('username')
        self.config['MYSQL_PASSWORD'] = mysql_cfg.get('password')
        self.config['MYSQL_DB'] = mysql_cfg.get('database')
        self.Mysql = MySQL(self)

        # Load gifts into memory and setup MySQL connection
        with self.app_context():
            self.GiftList = Gifts(self.Mysql)

        self.create_pages()

    def create_pages(self):
        # Render main page
        @self.route('/')
        def index():
            return render_template('index.html', menu=self.menu, gifts=self.GiftList.get())

        @self.route('/<section>')
        def load_section(section):
            print("Section:", section)
            return render_template(f'{section}.html')

        # Handle gift get_information request
        @self.route('/get_info', methods=['POST'])
        def get_info():
            name = request.form['name']
            self.GiftList.get_code(name)
            return [self.GiftList[name].title, generate_code(name)]

        # Handle gift claim request
        @self.route('/claim', methods=['POST'])
        def claim():
            name = request.form['name']
            code = request.form['code']

            if not self.GiftList.is_claimed(name):
                # Mark gift as claimed including database update
                self.GiftList.claim(name, code, request.remote_addr)
                return "success"
            else:
                return "error"

        # Handle gift free request
        @self.route('/free', methods=['POST'])
        def free():
            name = request.form['name']
            code = request.form['code']

            if not code:
                return "error"

            # If user entered correct code, free gift including database update
            if code.upper() == self.GiftList.get_code(name):
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

        # Try to get configurations to check if their syntax is correct
        connection_cfg = config["connection"]
        mysql_cfg = config["mysql"]

    except (FileNotFoundError, KeyError):
        # If file not foud or corrupted, create new from default
        with open(CONFIG_FILE_DEFAULT, "r", encoding="utf-8") as default_file:
            config:dict = yaml.load(default_file, Loader=yaml.Loader)

        
        # Create new config file with default values
        shutil.copyfile(CONFIG_FILE_DEFAULT, CONFIG_FILE)
        #with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        #    yaml.dump(config, file, Dumper=yaml.Dumper, sort_keys=False)

        # Get default connection and mysql configurations
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
