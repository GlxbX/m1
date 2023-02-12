from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests

from bs4 import BeautifulSoup as bs
import time
import datetime

from .DB import BaseDB
from .marketScanner import Scanner
from .priceAnalyzer import Analyzer
from .itemBuyer import Buyer
from .secure_data import log, pas



class TradeBot(Scanner,Analyzer, Buyer):
    def __init__(self):
        #подключение базы данных
        self.db = BaseDB()
        
        #переменные 
        self.balance = 0

        #login and password
        self.log = log 
        self.pas = pas

        #ID предметов для покупки
        self.items_for_trade = []
        self.items_stoplist = [935 ,985, 984, 942, 852, 554, 823, 556, 945, 558, 559, 564, 82, 199, 45, 73, 86, 46, 48, 105, 111, 97, 96, 208, 263, 390]

        # настройки webdriver
        self.options = webdriver.ChromeOptions()
        print
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--disable-software-rasterizer")
        self.options.add_argument("--disable-gpu")
        self.options.add_experimental_option("excludeSwitches", ['enable-logging'])
        self.options.headless = False
        self.service = Service("D:\Worktable\Izmaylov\Staff\Python\m1project\chromedriver")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.url = "https://monopoly-one.com/market"


    #аутентификация
    def authentificate(self):
        #страница аутентификациИ
        self.driver.get(url='https://monopoly-one.com/auth')
        time.sleep(5)

        #логгин
        log_input = self.driver.find_element(By.ID, "auth-form-email")
        log_input.clear()
        log_input.send_keys(self.log)
        time.sleep(5)

        #пароль
        pas_input = self.driver.find_element(By.ID, "auth-form-password")
        pas_input.clear()
        pas_input.send_keys(self.pas)
        time.sleep(3)

        #кнопка submit
        login_button = self.driver.find_element(By.CLASS_NAME  , "btn-ok").click()
        time.sleep(5)


    

    def start_cycle(self):


        #requests
        self.session = requests.Session()

        self.session.headers.update({"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"})
        for cookie in self.driver.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        
        
        #подключение к market
        self.driver.get(url=self.url)
        time.sleep(5)

        soup = self.get_bf4_source()
        self.balance = self.get_balance(soup)

        last_checked_item = [0,0]
        try:
            while True:
                start = time.time()

                sess = self.session.get("https://monopoly-one.com/api/market.getLastSellups?count=50")
                
                last_50_listings = sess.json()

                things = last_50_listings['data']['things']

                last_item = last_50_listings['data']['things'][0]

                #Получаем id и цену
                item_name = last_item['title']
                item_id = last_item['thing_prototype_id']
                price = last_item['price']
            
                current_item = [item_id, price]
            

                if last_checked_item != current_item:

                    wanted_price = self.db.get_wanted_price(item_id)
                    if price <= wanted_price and price <= self.balance/2:

                        if item_id not in self.items_stoplist:

                            print("Trying to buy ", item_name)
                            try_to_buy = self.buy(item_id, price)

                            if try_to_buy:
                                self.balance -= price
                                wanted_sell_price = round(((wanted_price*1.1)/85)*100,2)
                                self.db.add_new_transaction(item_id, item_name, price, wanted_sell_price)
                                print("Bought", item_name, price, "- wanted sell price - ", wanted_sell_price)
                                print(" ")
                            else:
                                print("Could not buy", item_name, price)
                                print(" ")

                    last_recorded_price = self.db.get_last_price(item_id)
                    if price != last_recorded_price:
                        qty = last_item['count']
                        now  = self.get_current_time()
                    

                        if wanted_price == -1:
                            self.db.add_new_item(item_id, item_name)
                        else:
                            wanted_price = self.update_items_info_wanted_price(item_id)

                        print("{} current price is {} - want {}".format(item_name, price, wanted_price))
                        print("")
                            

                        self.db.insert_new_data(price, qty, now, item_id)
                        print(22)
                last_checked_item = current_item


                for ident in range(1,50):
                    item = things[ident]

                    item_name = item['title']
                    item_id = item['thing_prototype_id']
                    price = item['price']


                    wanted_price = self.db.get_wanted_price(item_id)
                    last_recorded_price = self.db.get_last_price(item_id)
                    if price != last_recorded_price:
                        print('PRICE IS UP!  ',item_name, " current - ", price, "previous - ", last_recorded_price)
                        print('')
                        qty = item['count']
                        now  = self.get_current_time()
                        

                        if wanted_price == -1:
                            self.db.add_new_item(item_id, item_name)
                        else:
                            wanted_price = self.update_items_info_wanted_price(item_id)

                        self.db.insert_new_data(price, qty, now, item_id)

                algtime = round((time.time()-start),2)
               
                if algtime<1:
                    time.sleep(1-algtime)
                # print('ALGO TIME -- ',(round((time.time()-start),2)))
                
                
        except Exception as ex:
            print()
            print(ex)

        finally:
            self.driver.close()
            self.driver.quit()
            self.db.commit_and_close()

    def run(self):
        #подключение к базе данных
        self.db.connect()

        self.authentificate()
        
        self.start_cycle()
     