import yaml
import random
from zlib import crc32
from flask_mysqldb import MySQL
from MySQLdb import IntegrityError, OperationalError

GIFT_LIST_FILE = "static/yaml/gifts.yml"

OK = 0
ERR = -1

class MySQLBridge:
    def __init__(self, Mysql:MySQL):
        self.Mysql:MySQL = Mysql
        
        # Create gifts database table, if it doesnt exist
        try:
            self.create_table()
        except OperationalError as err:
            raise Exception("Database connection config is invalid."
                            + "Is it configured correctly?\n"
                            + str(err))
    
    def execute_query(self, query:str, params:tuple=None):
        cursor = self.Mysql.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        result = cursor.fetchall()
        self.Mysql.connection.commit()
        cursor.close()

        return result
    
    def create_table(self) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS gifts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            free_code VARCHAR(255),
            claimed BOOLEAN
        )
        """
        self.execute_query(query)
    
    def add_gift(self, name:str, free_code:str, claimed:bool) -> int:
        query = "INSERT INTO gifts (name, free_code, claimed) VALUES (%s, %s, %s)"
        try:
            self.execute_query(query, (name, free_code, claimed))
        except IntegrityError:
            print("Error: Database entry with name \""
                  + name + "\" already exists!")
            return ERR
        else:
            return OK
    
    def update_free_code(self, name:str, new_free_code:str) -> None:
        query = "UPDATE gifts SET free_code = %s WHERE name = %s"
        self.execute_query(query, (new_free_code, name))
    
    def update_claim_status(self, name:str, new_claim_status:bool) -> None:
        query = "UPDATE gifts SET claimed = %s WHERE name = %s"
        self.execute_query(query, (new_claim_status, name))
    
    def get_gift_info(self, name:str) -> tuple[str, int]:
        query = "SELECT free_code, claimed FROM gifts WHERE name = %s"
        result = self.execute_query(query, (name,))

        # Separate result tuple, parse claimed to bool and return separately
        code, claimed = result[0]
        return code, bool(claimed)
        
    def get_all_gifts(self) -> list:
        query = "SELECT name FROM gifts"
        result = self.execute_query(query)

        return [row[0] for row in result]


class Gift:
    def __init__(self, name:str, title:str, url:str, img:str, desc:str) -> None:
        self.title:str = title
        self.url:str = url
        self.img:str = img
        self.desc:str = desc

        self.free_code:str = self.generate_code(name)
        self.claimed:bool = False
    
    def __repr__(self) -> str:
        return f"\"{self.title}\", {'Claimed' if self.claimed else 'Available'} (" + self.free_code + ")"

    def generate_code(self, name:str) -> str:
        # Generate 0xRRDDDD code, where R is random and D is determined by name
        new_code = (crc32(name.encode('utf-8')) & 0xFFFF + (random.randint(0, 255) << 16))
        # Transform new code into 6 cipher hexa string
        new_code = f"{new_code:06X}"

        return new_code
    
    def to_dict(self) -> None:
        return {"title": self.title, "url": self.url, "img": self.img,
                "claimed": self.claimed, "desc": self.desc}
    
    def claim(self, code:str) -> None:
        self.claimed = True
        self.free_code = code
    
    def free(self) -> None:
        self.claimed = False

    def update_attributes(self, free_code:str=None, new_status:bool=None):
        if free_code is not None:
            self.free_code = free_code
        if new_status is not None:
            self.claimed = new_status

class Gifts:
    def __init__(self, Mysql:MySQL) -> None:
        self.gift_dict:dict = {}

        with open(GIFT_LIST_FILE, "r", encoding="utf-8") as file:
            gifts = yaml.load(file, Loader=yaml.Loader)

        # Load gifts configuration
        try:
            for gift in gifts:
                self.gift_dict[gift] = Gift(gift, **gifts[gift])
        except TypeError as err:
            raise Exception("Syntax Error in " + GIFT_LIST_FILE + " file.\n" + str(err))
        
        # Load gifts configuration
        self.MysqlBridge = MySQLBridge(Mysql)
        self.MysqlBridge.get_all_gifts()

        # Get all gifts from database and synchronize them with self.gift_dict
        gifts_in_db:list = self.MysqlBridge.get_all_gifts()
        for gift in gifts:
            # If gift already in db, read their free_code and claim status
            if gift in gifts_in_db:
                code, claimed = self.MysqlBridge.get_gift_info(gift)
                self.gift_dict[gift].update_attributes(free_code=code, new_status=claimed)
            # Else add gift into the database with default values
            else:
                self.MysqlBridge.add_gift(gift, self.gift_dict[gift].free_code, False)

    def __repr__(self) -> str:
        return "\n".join(str(key) + ": "
                         + str(self.gift_dict[key]) for key in self.gift_dict)
    
    def __getitem__(self, name: str) -> Gift:
        return self.gift_dict[name]

    def update_database(self, name:str, free_code:str=None, new_status:bool=None):
        if free_code is not None:
            self.MysqlBridge.update_free_code(name, free_code)
            
        if new_status is not None:
            self.MysqlBridge.update_claim_status(name, new_status)

    def get(self):
        ret_ls = []
        for key in self.gift_dict:
            gift:Gift = self.gift_dict[key]
            ret_ls.append({"name": key} | gift.to_dict())

        return ret_ls
    
    def get_code(self, name:str) -> str:
        test = self.MysqlBridge.get_gift_info(name)
        return test[0]
    
    def is_claimed(self, name:str) -> bool:
        test = self.MysqlBridge.get_gift_info(name)
        return test[1]
    
    def claim(self, name:str, code:str) -> None:
        # Update class attribute claim status
        gift:Gift = self.gift_dict[name]
        gift.claim(code)
        self.gift_dict[name] = gift

        # Update database information claim status
        self.update_database(name, free_code=code, new_status=True)
    
    def free(self, name:str) -> None:
        # Update class attribute claim status
        gift:Gift = self.gift_dict[name]
        gift.free()
        self.gift_dict[name] = gift

        # Update database information claim status
        self.update_database(name, new_status=False)
