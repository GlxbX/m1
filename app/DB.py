import sqlite3


# class BaseDatabase:
#     def __init__(self):
#         pass

#     def connect(self):
#         self.con = sqlite3.connect(self.database,isolation_level=None)
#         self.cur = self.con.cursor()

#     def commit_and_close(self):
#         self.cur.close()
#         self.con.close()
#         self.con = None 
#         self.cur = None

class BaseDB:
    def __init__(self):
        self.database = "GraphsData.sqlite"
        self.con = None 
        self.cur = None

    def connect(self):
        self.con = sqlite3.connect(self.database,isolation_level=None)
        self.cur = self.con.cursor()

    def commit_and_close(self):
        self.cur.close()
        self.con.close()
        self.con = None 
        self.cur = None
    
    def add_new_item(self,i_id,i_name):
        insertQuery = """INSERT INTO items_info VALUES (?, ?, ?);"""
        self.cur.execute(insertQuery, (i_id,i_name,0))

    def get_item_name_by_id(self,id):
        item_name = self.cur.execute("SELECT item_name FROM items_info WHERE item_id == {}".format(id)).fetchone()[0]
        return item_name


    def get_buy_price_limit(self,i_id):
        price = self.cur.execute("""SELECT item_wanted_buy_price from items_info WHERE item_id = {};""".format(i_id)).fetchone()
        return 0 if price==None else price[0]
    

    def create_new_item_table(self, id):
        self.cur.execute("CREATE TABLE IF NOT EXISTS item{} (price FLOAT, qty INTEGER, dt DATETIME)".format(id))
        

    def get_last_price(self,id):
        self.create_new_item_table(id)
        price = self.cur.execute("SELECT price FROM item{}".format(id)).fetchall()
        return 0 if price == [] else list(reversed(price))[0][0]

    def insert_new_data(self, price, qty ,timestamp, id):
        insertQuery = """INSERT INTO item{} VALUES (?, ?, ?);""".format(id)
        self.cur.execute(insertQuery, (price, qty,timestamp))
        
    def get_daily_prices(self,i_id, start_time):
        L = self.cur.execute("""SELECT price from item{} WHERE dt > '{}' """.format(i_id,start_time)).fetchall()
        return [i[0] for i in L]


    def update_wanted_price(self, i_id, price):
        self.cur.execute("""UPDATE items_info SET item_wanted_buy_price = {} WHERE item_id = {};""".format(price, i_id))

    def get_recorded_items(self):
        L = self.cur.execute("""SELECT item_id FROM items_info""").fetchall()
        return [i[0] for i in L]

    def get_wanted_price(self,i_id):
        wp = self.cur.execute("""SELECT item_wanted_buy_price from items_info WHERE item_id = {}""".format(i_id)).fetchone()
        
        return wp[0] if wp!= None else -1

# class AnalyzerDB(BaseDatabase):
#     def __init__(self):
#         self.database = "GraphsData.sqlite"
#         self.con = None 
#         self.cur = None

#     def get_daily_prices(self,i_id, start_time):
#         L = self.cur.execute("""SELECT price from item{} WHERE dt > '{}' """.format(i_id,start_time)).fetchall()
#         return [i[0] for i in L]

#     def check_for_item_info(self,i_id):
#         a = self.cur.execute("""SELECT count(*) from items_info WHERE item_id = {}""".format(i_id))
#         return 0 if a == 0 else 1

#     def update_wanted_price(self, i_id, price):
#         if self.check_for_item_info(i_id) == 1:
#             self.cur.execute("""UPDATE items_info SET item_wanted_buy_price = {} WHERE item_id = {};""".format(price, i_id))



# a = Database()
# a.connect()
# price = a.get_last_price(36)
# print(price)