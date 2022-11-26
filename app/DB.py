import sqlite3


class Database:
    def __init__(self):
        self.database = "GraphsData.sqlite"
        self.con = None 
        self.cur = None

    def connect(self):
        self.con = sqlite3.connect(self.database,isolation_level=None)
        self.cur = self.con.cursor()
        
    
    def create_new_item_table(self, id):
        self.cur.execute("CREATE TABLE IF NOT EXISTS item{} (price FLOAT, dt DATETIME)".format(id))

    def insert_new_data(self, price, timestamp, id):
        insertQuery = """INSERT INTO item{} VALUES (?, ?);""".format(id)
        self.cur.execute(insertQuery, (price, timestamp))
    
    def add_new_transaction(self,item_id, price, b_time, listed_price):
        insertQuery = """INSERT INTO transactions (item_id, buy_price, buy_time, listed_price) VALUES (?, ?, ?,?);"""
        self.cur.execute(insertQuery, (item_id, price,b_time, listed_price))

    def add_listing_to_transaction(self,t_id):
        self.cur.execute("""UPDATE transactions SET is_listed = 1 WHERE trans_id == {};""".format(t_id))
        

    def get_item_name_by_id(self,id):
        item_name = self.cur.execute("SELECT item_name FROM items_info WHERE item_id == {}".format(id)).fetchone()[0]
        return item_name
    
    def get_min_listing_price(self):
        a = self.cur.execute("SELECT COUNT(trans_id) FROM transactions WHERE is_listed == 0").fetchone()[0]

        if a == 0:
            return -1, 99999
        else:
            f = self.cur.execute("SELECT trans_id, listed_price FROM transactions WHERE is_listed == 0 AND listed_price == (SELECT min(listed_price) FROM transactions WHERE is_listed ==0)").fetchone()
            return f[0],float(f[1])


    def commit_and_close(self):
        self.cur.close()
        self.con.close()
        self.con = None 
        self.cur = None
    
   