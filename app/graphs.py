import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import sqlite3
from DB import Database


ID = 345


class Chart:
    def __init__(self, ID):
        db = Database()
        db.connect()
        df = pd.read_sql_query("SELECT price, dt from item{}".format(ID), db.con)
        plt.plot(df['dt'], df['price'], color='red', marker='o')
       
        title = db.get_item_name_by_id(ID)
        plt.title( title , fontsize=14)
        plt.xticks(rotation=30, ha='right')
        plt.xlabel('Time', fontsize=10)
        plt.ylabel('Price', fontsize=14)
        plt.grid(True)

    def show(self):
        plt.show()

chart = Chart(ID)
chart.show()


