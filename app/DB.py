import sqlite3


class Database:
    def __init__(self):
        self.database = "GraphsData.sqlite"
        self.con = None 
        self.cur = None

    def connect(self):
        self.con = sqlite3.connect(self.database,isolation_level=None)
        self.cur = self.con.cursor()
        
    def get_buy_price_limit(self,i_id):
        price = self.cur.execute("""SELECT item_wanted_buy_price from items_info WHERE item_id = {};""".format(i_id)).fetchone()
        return 0 if price==None else price[0]
        
    def create_new_item_table(self, id):
        self.cur.execute("CREATE TABLE IF NOT EXISTS item{} (price FLOAT, dt DATETIME)".format(id))
        

    def get_last_price(self,id):
        price = self.cur.execute("SELECT price FROM item{}".format(id)).fetchall()
        return 0 if price == [] else list(reversed(price))[0][0]

    def insert_new_data(self, price, timestamp, id):
        self.create_new_item_table(id)
        last_price = self.get_last_price(id)
        if price != last_price:
            insertQuery = """INSERT INTO item{} VALUES (?, ?);""".format(id)
            self.cur.execute(insertQuery, (price, timestamp))
        

    def commit_and_close(self):
        self.cur.close()
        self.con.close()
        self.con = None 
        self.cur = None
    
# a = Database()
# a.connect()
# price = a.get_last_price(36)
# print(price)