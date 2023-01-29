from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime

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

        #настройки webdriver
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")
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


    def run(self):
        #подключение к базе данных
        self.db.connect()

        self.authentificate()
        
        try:
            #подключение к market
            self.driver.get(url=self.url)
            time.sleep(5)

            last_checked_item = [0,0]
            while True:
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'list-one.marketThing'))
                WebDriverWait(self.driver, 60).until(element_present)

                self.balance = float(self.driver.find_element(By.CLASS_NAME, 'market-balance-sum').text[:-3])

                market_listings = [self.get_current_market_listings()]
                
                for listing in market_listings:
                    #Получаем id и цену
                    item_id = self.get_item_id(listing)
                    price = self.get_item_price(listing)

                    current_item = [item_id, price]

                    if last_checked_item != current_item:

                        wanted_price = self.get_wanted_price(item_id)
                        if price <= wanted_price and price <= self.balance:
                            print("------------------------------------------Trying to buy ", item_name)
                            self.buy(item_id, price)

                        last_recorded_price = self.db.get_last_price(item_id)
                        if price != last_recorded_price:
                            qty = self.get_item_qty(listing)
                            now  = self.get_current_time()
                            item_name = self.get_item_name(listing)

                            if wanted_price == -1:
                                self.db.add_new_item(item_id, item_name)
                            else:
                                wanted_price = self.update_items_info_wanted_price(item_id)

                            print("{} current price is {} - want {}".format(item_name, price, wanted_price))
                            print("")
                            

                            self.db.insert_new_data(price, qty, now, item_id)

                    last_checked_item = current_item

                # time.sleep(1)
                self.driver.refresh()

        except Exception as ex:
            print(ex, "try_cycle_err")

        finally:
            self.driver.close()
            self.driver.quit()
            self.db.commit_and_close()