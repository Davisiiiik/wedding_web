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
        # Execute query
        cursor.execute(query, params)

        # Get all return data and commit changes to database
        result = cursor.fetchall()
        self.Mysql.connection.commit()
        cursor.close()

        return result
    
    def create_table(self) -> None:
        # Create a database table if it doesnt exist
        query = """
        CREATE TABLE IF NOT EXISTS gifts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            free_code VARCHAR(255),
            claimed BOOLEAN,
            claim_ip_addr VARCHAR(255)
        )
        """
        self.execute_query(query)
    
    def add_gift(self, name:str) -> int:
        # Add new gift into the database with default values
        query = "INSERT INTO gifts (name, claimed) VALUES (%s, %s)"
        try:
            self.execute_query(query, (name, False))
        except IntegrityError:
            # Since gifts MUST be unique by name, return error on duplicity
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
    
    def update_claim_ip_addr(self, name:str, claim_ip_addr:bool) -> None:
        query = "UPDATE gifts SET claim_ip_addr = %s WHERE name = %s"
        self.execute_query(query, (claim_ip_addr, name))
    
    def get_gift_info(self, name:str) -> tuple[str, int]:
        query = "SELECT free_code, claimed, claim_ip_addr FROM gifts WHERE name = %s"
        result = self.execute_query(query, (name,))

        # Separate result tuple, parse claimed to bool and return separately
        code, claimed, claim_ip_addr = result[0]
        return code, bool(claimed), claim_ip_addr
        
    def get_all_gifts(self) -> list:
        query = "SELECT name FROM gifts"
        result = self.execute_query(query)

        return [row[0] for row in result]


class Gift:
    def __init__(self, name:str, title:str, url:str, img:str, desc:str) -> None:
        self.name:str = name
        self.title:str = title
        self.url:str = url
        self.img:str = img
        self.desc:str = desc
    
    def __repr__(self) -> str:
        return f"{self.name}: \"{self.title}\", {self.desc}"
    
    def to_dict(self) -> None:
        return {"name": self.name, "title": self.title, "desc": self.desc,
                "url": self.url, "img": self.img}


class Gifts:
    def __init__(self, Mysql:MySQL) -> None:
        self.gift_list:list = []

        # Load gifts from yaml file
        with open(GIFT_LIST_FILE, "r", encoding="utf-8") as file:
            gifts = yaml.load(file, Loader=yaml.Loader)

        # Load gifts configuration
        try:
            for gift in gifts:
                self.gift_list.append(Gift(gift, **gifts[gift]))
        except TypeError as err:
            raise Exception("Syntax Error in " + GIFT_LIST_FILE + " file.\n"
                            + str(err))
        
        # Load gifts configuration
        self.MysqlBridge = MySQLBridge(Mysql)
        self.MysqlBridge.get_all_gifts()

        # Get all gifts from database and check if any gift loaded from yaml
        # config is not missing
        gifts_in_db:list = self.MysqlBridge.get_all_gifts()
        for gift in gifts:
            # If gift is not in database, add it with default values
            if gift not in gifts_in_db:
                self.MysqlBridge.add_gift(gift)

    def __repr__(self) -> str:
        return "\n".join(str(gift) for gift in self.gift_list)
    
    def __getitem__(self, name:str) -> Gift|None:
        item:Gift
        for item in self.gift_list:
            if item.name == name:
                return item
        return None

    def update_database(self, name:str, free_code:str=None, new_status:bool=None, claim_ip_addr:str=None):
        if free_code is not None:
            self.MysqlBridge.update_free_code(name, free_code)
            
        if new_status is not None:
            self.MysqlBridge.update_claim_status(name, new_status)
            
        if claim_ip_addr is not None:
            self.MysqlBridge.update_claim_ip_addr(name, claim_ip_addr)

    def get(self):
        ret_ls = []
        gift:Gift
        for gift in self.gift_list:
            claimed = self.is_claimed(gift.name)
            ret_ls.append(gift.to_dict() | {"claimed": claimed})

        return ret_ls
    
    def get_code(self, name:str) -> str:
        test = self.MysqlBridge.get_gift_info(name)
        return test[0]
    
    def is_claimed(self, name:str) -> bool:
        test = self.MysqlBridge.get_gift_info(name)
        return test[1]
    
    def get_claim_ip_addr(self, name:str) -> bool:
        test = self.MysqlBridge.get_gift_info(name)
        return test[2]
    
    def claim(self, name:str, code:str, ip_addr:str) -> None:
        # Update gift information in database and set claim status to true
        self.update_database(name, free_code=code, new_status=True,
                             claim_ip_addr=ip_addr)
    
    def free(self, name:str) -> None:
        # Reset gift claim status in database
        self.update_database(name, new_status=False)


def generate_code(name:str) -> str:
    """Generates a 6 digit hexadecimal code from given name

    Args:
        name (str): Name from which the code will be generated

    Returns:
        str: Generated 6 digit hexadeciaml code
    """
    # Generate 0xRRDDDD code, where R is random and D is determined by name
    new_code = (crc32(name.encode('utf-8')) & 0xFFFF
                + (random.randint(0, 255) << 16))
    # Transform new code into 6 cipher hexa string and return
    return f"{new_code:06X}"