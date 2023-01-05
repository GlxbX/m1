from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime


from .DB import Database 

# from multiprocessing import Pool

class Scanner:
    def __init__(self):

        #подключение базы данных
        self.db = Database()

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

    def beautify_price(self,pr:str):
        l = pr.replace('\u2009', '')
        a = l
        return float(a)

        #запуск сканера
    def run(self):
        #подключение к базе данных
        self.db.connect()

        #запуск
        try:
            #подключение к market
            self.driver.get(url=self.url)
            time.sleep(5)
            
            while True:
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'list-one.marketThing'))
                WebDriverWait(self.driver, 30).until(element_present)

                source_data = self.driver.page_source
                soup = bs(source_data, "lxml")
                item_list = soup.find_all("a", class_="list-one marketThing")
                
                for i in item_list[:3]:
                    item_id = int(i.get('href')[14:]) 
                    price = self.beautify_price(i.find("div", class_ ="marketThing-price").text[3:-9])

                    #текущее время
                    now = datetime.now()
                    now = datetime.strftime(now, "%d/%m/%Y %H:%M:%S")
                    
                    #записать цену в бд, если были изменения
                    self.db.insert_new_data(price, now, item_id)
                  
                    # wanted_price = self.db.get_buy_price_limit(item_id)
            
                    # print(item_id," curr= ", price," want- ", wanted_price)
                
                    # if self.balance>price:
                    #     if price <= wanted_price < 6:
                            
                    #         self.buy(item_id,price)

                # self.driver.refresh()
                time.sleep(1)
                self.driver.refresh()

        except Exception as ex:
            print(ex, "try_cycle_err")

        finally:
            self.driver.close()
            self.driver.quit()
            self.db.commit_and_close()