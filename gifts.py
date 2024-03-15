import yaml
import random
from zlib import crc32

GIFT_LIST_FILE = "gifts.yml"

class Gift:
    def __init__(self, name:str, title:str, url:str, img:str, desc:str) -> None:
        self.title:str = title
        self.url:str = url
        self.img:str = img
        self.desc:str = desc

        self.free_code:str = self.generate_code(name, False)
        self.claimed:bool = False
    
    def __repr__(self) -> str:
        return f"\"{self.title}\", {'Claimed' if self.claimed else 'Available'} ({self.free_code:X})"

    def generate_code(self, name:str, update:bool=True) -> str:
        # Generate 0xRRDDDD code, where R is random and D is determined by name
        new_code = (crc32(name.encode('utf-8')) & 0xFFFF + (random.randint(0, 255) << 16))
        # Transform new code into 6 cipher hexa string
        new_code = f"{new_code:06X}"

        if update:
            self.free_code = new_code
        return new_code
    
    def to_dict(self) -> None:
        return {"title": self.title, "url": self.url, "img": self.img,
                "claimed": self.claimed, "desc": self.desc}
    
    def claim(self) -> None:
        self.claimed = True
    
    def free(self) -> None:
        self.claimed = False

    def update_database(self, name:str, new_status:bool):
        pass


class Gifts:
    def __init__(self) -> None:
        self.gift_dict = {}

        with open(GIFT_LIST_FILE, "r", encoding="utf-8") as file:
            gifts = yaml.load(file, Loader=yaml.Loader)

        try:
            for gift in gifts:
                self.gift_dict[gift] = Gift(gift, **gifts[gift])
        except TypeError as err:
            raise Exception("Syntax Error in " + GIFT_LIST_FILE + " file.\n", err)

    def __repr__(self) -> str:
        return "\n".join(str(key) + ": "
                         + str(self.gift_dict[key]) for key in self.gift_dict)
    
    def __getitem__(self, name: str) -> Gift:
        return self.gift_dict[name]

    def update_database(self, name:str, new_status:bool):
        pass

    def get(self):
        ret_ls = []
        for key in self.gift_dict:
            gift:Gift = self.gift_dict[key]
            ret_ls.append({"name": key} | gift.to_dict())

        return ret_ls
    
    def claim(self, name:str) -> None:
        # Update class attribute claim status
        gift:Gift = self.gift_dict[name]
        gift.claim()
        self.gift_dict[name] = gift

        # Update database information claim status
        self.update_database(name, True)
    
    def free(self, name:str) -> None:
        # Update class attribute claim status
        gift:Gift = self.gift_dict[name]
        gift.free()
        self.gift_dict[name] = gift

        # Update database information claim status
        self.update_database(name, False)

    
def main():
    App = Gifts()
    print(App.get())

if __name__ == '__main__':
    main()
