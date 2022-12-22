from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
import pandas as pd 
from DB import Database 
from secure_data import log, pas
from multiprocessing import Pool


class Scanner:
    def __init__(self,log,pas):

        #переменные 
        self.balance = 0

        #подключение базы данных
        self.db = Database()

        #параметры сканера
        self.log = log 
        self.pas = pas
        self.wanted_profit_percent = 2 

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

    #скрипт покупки item
    def buy(self,id,price):
        item_url = "https://monopoly-one.com/market/thing/{}".format(id)
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(item_url)

        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'marketThing-price'))
        WebDriverWait(self.driver, 10).until(element_present)
        

        pr = self.driver.find_element(By.CLASS_NAME,"marketThing-price").text[:-3]
    
        curr_price = float(pr)

        # source_data = self.driver.page_source
        # soup = bs(source_data, "lxml")

        # curr_price = soup.find("div", class_ = "marketThing-price")
        # curr_price = float(curr_price.text[:-3])

        while curr_price<=price:
            #нажать кнопку купить
            self.driver.find_element(By.CLASS_NAME, "button.button-small.button-grass").click()

            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-small.btn-error'))
            WebDriverWait(self.driver, 10).until(element_present)
           

            #нажать кнопку подтверждения купить
            self.driver.find_element(By.CLASS_NAME, "btn.btn-small.btn-error").click()
            self.balance-=price
            
            time.sleep(1)


            self.driver.refresh()

            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'marketThing-price'))
            WebDriverWait(self.driver, 10).until(element_present)

            pr = self.driver.find_element(By.CLASS_NAME,"marketThing-price").text[:-3]
            curr_price = float(pr)
            time.sleep(1)
            
       
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(1)
      
   
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
        

    #запуск сканера
    def run(self):
        #подключение к базе данных
        self.db.connect()

        #аутентификация
        self.authentificate()

        #запуск
        try:
            #подключение к странице item
            self.driver.get(url=self.url)
            time.sleep(5)
            
            while True:
                
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'list-one.marketThing'))
                WebDriverWait(self.driver, 10).until(element_present)

                self.balance = float(self.driver.find_element(By.CLASS_NAME, 'market-balance-sum').text[:-3])

                source_data = self.driver.page_source
                self.driver.refresh()

                soup = bs(source_data, "lxml")
                item_list = soup.find_all("a", class_="list-one marketThing")
                
                for i in item_list[:3]:
                    item_id = int(i.get('href')[14:])


                    a = i.find("div", class_ ="marketThing-price").text[3:-9]
                    
                    print(''.join(a.split(' ')))
                    print(a.replace("\u2009", ""))
                    a = a.replace("\u2009", "")
                    

                    price = float(a)
                    wanted_price = self.db.get_buy_price_limit(item_id)
                  
                    # print(item_id," curr= ", price," want- ", wanted_price)

                    

                    if self.balance>price:
                        if price <= wanted_price:
                            print("------------------------------------ Bought", item_id, price)
                            self.buy(item_id,price)

                # self.driver.refresh()
                time.sleep(1) 

        except Exception as ex:
            print(ex, "try_cycle_err")

        finally:
            self.driver.close()
            self.driver.quit()

if __name__ == "__main__":
    scanner = Scanner(log, pas)
    scanner.run()

   
