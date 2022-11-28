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
    
    def update_listing_price(self, t_id, sell_price):
        self.cur.execute("""UPDATE transactions SET listed_price = {} WHERE trans_id = {};""".format(sell_price, t_id))
        

    def update_sold_items(self, p, i_id):
        num_of_sold_items = self.cur.execute("""SELECT COUNT(trans_id) FROM transactions WHERE is_sold = 0 and is_listed = 1 and listed_price < {} and item_id = {};""".format(p, i_id)).fetchone()[0]
        self.cur.execute("""UPDATE transactions SET is_sold = 1 ,profit = listed_price*0.85-buy_price WHERE is_sold = 0 and is_listed =1 and listed_price <  {};""".format(p))
        return num_of_sold_items

    def get_item_name_by_id(self,id):
        item_name = self.cur.execute("SELECT item_name FROM items_info WHERE item_id == {}".format(id)).fetchone()[0]
        return item_name
    
    def get_min_listing_price(self,i_id):
        a = self.cur.execute("SELECT COUNT(trans_id) FROM transactions WHERE is_listed == 0 and item_id = {}".format(i_id)).fetchone()[0]

        if a == 0:
            return -1, 99999
        else:
            f = self.cur.execute("SELECT trans_id, listed_price FROM transactions WHERE is_listed == 0 AND item_id = {} AND listed_price == (SELECT min(listed_price) FROM transactions WHERE is_listed ==0)".format(i_id)).fetchone()
            return f[0],float(f[1])


    def commit_and_close(self):
        self.cur.close()
        self.con.close()
        self.con = None 
        self.cur = None
    
   