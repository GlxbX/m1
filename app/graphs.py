import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import sqlite3
from DB import BaseDB
from timeManager import TimeManager


ID = 566

class Chart:
    def __init__(self, ID):
        db = BaseDB()
        db.connect()

        tm = TimeManager()

        st = tm.get_start_time(9)
        now = tm.get_current_time()
        df = pd.read_sql_query("SELECT qty, price, dt from item{} WHERE dt BETWEEN '{}' and '{}' ".format(ID, st, now), db.con)

        coef = [df['price'][i] * df['qty'][i] for i in range(len(df))]

        fig,ax = plt.subplots()
        # make a plot
        ax.plot(df['dt'],
                df['price'],
                color="red", 
                marker="o")
        # set x-axis label
        ax.set_xlabel("datetime", fontsize = 10)
        # set y-axis label
        ax.set_ylabel("price",
                    color="red",
                    fontsize=14)


        # twin object for two different y-axis on the sample plot
        ax2=ax.twinx()
        # make a plot with different y-axis using second axis object
        ax2.plot(df['dt'], df["qty"],color="blue",marker="o")
        ax2.set_ylabel("qty",color="blue",fontsize=14)
        # plt.show()
      

        # plt.plot(df['dt'] ,df['price'] ,color='red', marker='o')
       
        # title = db.get_item_name_by_id(ID)



        # plt.title( title , fontsize=14)
        # plt.xticks(rotation=30, ha='right')
        # plt.xlabel('Time', fontsize=10)
        # plt.ylabel('Price', fontsize=14)
        # plt.grid(True)

    def show(self):
        plt.show()

chart = Chart(ID)
chart.show()


