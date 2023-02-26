import sqlite3


class BaseDB:
    def __init__(self):
        self.database = "GraphsData.sqlite"
        self.con = None 
        self.cur = None

    #common
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

    def get_last_qty(self,id):
        self.create_new_item_table(id)
        qty = self.cur.execute("SELECT qty FROM item{}".format(id)).fetchall()
        return 0 if qty == [] else list(reversed(qty))[0][0]

    def insert_new_data(self, price, qty ,timestamp, id):
        insertQuery = """INSERT INTO item{} VALUES (?, ?, ?);""".format(id)
        self.cur.execute(insertQuery, (price, qty,timestamp))
        
    def get_daily_prices(self,i_id, start_time, now):
        L = self.cur.execute("""SELECT price from item{} WHERE dt BETWEEN '{}' and '{}' """.format(i_id,start_time, now)).fetchall()
        return [i[0] for i in L]

    def update_wanted_price(self, i_id, price):
        self.cur.execute("""UPDATE items_info SET item_wanted_buy_price = {} WHERE item_id = {};""".format(price, i_id))

    def get_recorded_items(self):
        L = self.cur.execute("""SELECT item_id FROM items_info""").fetchall()
        return [i[0] for i in L]

    def get_wanted_price(self,i_id):
        wp = self.cur.execute("""SELECT item_wanted_buy_price from items_info WHERE item_id = {}""".format(i_id)).fetchone()
        return wp[0] if wp!= None else -1

    def get_items_for_sale(self):
        items = self.cur.execute("""SELECT thing_id, thing_name, buy_price, wanted_sell_price FROM transactions WHERE is_listed = 0""").fetchall()
        return 0 if items == [] else items

    def add_new_transaction(self, thing):
        insertQuery = """INSERT INTO transactions (thing_id, thing_name ,buy_price, wanted_sell_price) VALUES (?, ?, ?, ?);"""
        self.cur.execute(insertQuery, (thing.id, thing.name, thing.buy_price, thing.wanted_sell_price))

    def get_t_counter(self, acc_id):
        return self.cur.execute("""SELECT t_count FROM accounts WHERE acc_id = {}""".format(acc_id)).fetchone()[0]

    def update_t_counter(self, acc_id, counter):
        self.cur.execute("""UPDATE accounts SET t_count = {} WHERE acc_id = {}""".format(counter, acc_id))

    def get_b_price_by_thing_id(self, t_id):
        return self.cur.execute("""SELECT buy_price FROM transactions WHERE thing_id = {}""".format(t_id)).fetchone()[0]

    def get_t_ids(self):
        return self.cur.execute("""SELECT thing_id FROM transactions WHERE is_sold = 0 """).fetchall()

    def update_sold_transactions(self, thing_id, res_price, dt):
        b_price = self.get_b_price_by_thing_id(thing_id)
        profit = round((res_price - b_price),2)
        d = {'rm': res_price, 'profit': profit, 'dt': dt, 't_id': thing_id}
        self.cur.execute("""UPDATE transactions SET recieved_money =:rm, profit =:profit, is_sold = 1, sold_time =:dt WHERE thing_id =:t_id;""", d)


    # def DELETE(self):
    #     nums = self.cur.execute("""SELECT item_id from items_info""").fetchall()
    #     nums = [i[0] for i in nums]
    #     for i in nums:

    #         self.cur.execute("""DELETE FROM item{} WHERE dt BETWEEN '29/01/2023 15:47:09' and '29/01/2023 20:56:01' """.format(i))