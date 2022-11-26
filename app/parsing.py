from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
import pandas as pd 
from DB import Database 
########
import matplotlib.pyplot as plt
#########
from secure_data import log, pas

class Scanner:
    def __init__(self,log,pas):
        self.db = Database()
        self.log = log 
        self.pas = pas
        self.id = None
        self.buy_limit = 5.61
        self.wanted_profit_percent = 2 
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--disable-software-rasterizer")
        self.options.headless = False
        self.service = Service("..chromedriver")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.url = "https://monopoly-one.com/market/thing/{}".format(self.id)

    def set_id(self,id):
        self.id = id 
        self.url = "https://monopoly-one.com/market/thing/{}".format(self.id)

    def get_sell_price(self, buy_price):
        return round(((buy_price/(85-self.wanted_profit_percent))*100),2)

    def buy(self,price, b_time):
        self.driver.find_element(By.CLASS_NAME, "button.button-small.button-grass").click()
        time.sleep(1)

        self.driver.find_element(By.CLASS_NAME, "btn.btn-small.btn-error").click()
        time.sleep(1)

        self.driver.refresh()

        listed_price = self.get_sell_price(price)

        self.db.add_new_transaction(self.id, price, b_time, listed_price)

    def sell(self, t_id, sell_price):
        #открыть отдельную вкладку - ссылка https://monopoly-one.com/inventory
        inv_url = "https://monopoly-one.com/inventory"
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(inv_url)
        time.sleep(5)

        #найти предмет по по поиску
        item_name = self.db.get_item_name_by_id(self.id)
        search_input = self.driver.find_element(By.XPATH, "//input[@autocomplete='off']")
        search_input.clear()
        search_input.send_keys(item_name)
        time.sleep(5)

        #найти предмет по классу
        item = self.driver.find_element(By.CLASS_NAME, "_img")
        item.click()
        time.sleep(5)

        #нажать "продать на маркете"
        sell_on_market = self.driver.find_element(By.XPATH, "//div[text()='Продать на Маркете']")
        sell_on_market.click()
        time.sleep(5)

        #ввести цену для покупателя
        input_price_for_customer = self.driver.find_element(By.CLASS_NAME, "form-input")
        input_price_for_customer.clear()
        input_price_for_customer.send_keys(sell_price)
        time.sleep(5)

        #продать 
        button_sell = self.driver.find_element(By.CLASS_NAME, "btn.btn-small.btn-ok")
        button_sell.click()
        time.sleep(5)

        #обновить инфу в транзакцию
        self.db.add_listing_to_transaction(t_id)

        #закрыть вкладку
        self.driver.close()
        #вернуть на прошлую вкладку
        self.driver.switch_to.window(self.driver.window_handles[0])



    def authentificate(self):
        self.driver.get(url='https://monopoly-one.com/auth')
        time.sleep(5)

        log_input = self.driver.find_element(By.ID, "auth-form-email")
        log_input.clear()
        log_input.send_keys(self.log)
        time.sleep(5)

        pas_input = self.driver.find_element(By.ID, "auth-form-password")
        pas_input.clear()
        pas_input.send_keys(self.pas)
        time.sleep(3)

        login_button = self.driver.find_element(By.CLASS_NAME  , "btn-ok").click()
        time.sleep(5)
        

    def run(self, minutes):
        
        self.db.connect()
        self.db.create_new_item_table(self.id)
        self.authentificate()

        try:
            last_price = 0 

         
            self.driver.get(url=self.url)
            time.sleep(5)

            for i in range(minutes*6):
                source_data = self.driver.page_source
                soup = bs(source_data, "lxml")

                min_listing_id, min_listing_price = self.db.get_min_listing_price()
                print(min_listing_price)

                curr_price = soup.find("div", class_ = "marketThing-price")
                while curr_price == None:
                    curr_price = soup.find("div", class_ = "marketThing-price")

                curr_price = float(curr_price.text[:-3])
                now = datetime.now()
                now = datetime.strftime(now, "%d/%m/%Y %H:%M:%S")

                #buy if price is below limit 
                if curr_price<self.buy_limit:
                    self.buy(curr_price, now)
                    print("------ +1 Item -------")
                    time.sleep(2)

                #sell if price is above limit
                if curr_price>min_listing_price:

                    self.sell(min_listing_id, min_listing_price)
                    print("------- Listed 1 item ------")
                    time.sleep(2)
                    
                    

                if last_price == 0:
                    last_price = curr_price
                else:
                    if curr_price<=last_price:
                        last_price = curr_price
                    else:
                        self.db.insert_new_data(last_price, now, self.id)
                        last_price = curr_price
  

                self.driver.refresh()
                time.sleep(10) 
                print(i)
       
            self.db.commit_and_close()
            title = soup.find("div", class_ = "marketListing-info-header-title").text

        except Exception as ex:
            print(ex)

        finally:
            self.driver.close()
            self.driver.quit()


if __name__ == "__main__":
    scanner = Scanner(log,pas)
    scanner.set_id(346)
    scanner.run(120)



  