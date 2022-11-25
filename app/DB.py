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
      
    def commit_and_close(self):
        self.cur.close()
        self.con.close()
        self.con = None 
        self.cur = None
    
    def commit(self):
        self.con.commit()