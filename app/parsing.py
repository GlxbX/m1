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
        self.log = log 
        self.pas = pas
        self.id = None 
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

    def buy(self):
        self.driver.find_element(By.CLASS_NAME, "button.button-small.button-grass").click()
        time.sleep(1)
        self.driver.find_element(By.CLASS_NAME, "btn.btn-small.btn-error").click()


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
        db = Database()
        db.connect()
        db.create_new_item_table(self.id)
        self.authentificate()

        try:
            priceLine = []
            timeLine = []

            self.driver.get(url=self.url)
            time.sleep(5)

            for i in range(minutes*6):
                source_data = self.driver.page_source
                soup = bs(source_data, "lxml")

                last_price = soup.find("div", class_ = "marketThing-price")
                last_price = float(last_price.text[:-3])

                limit = 5.61
                if last_price<limit:
                    self.buy()
                    time.sleep(2)

                now = datetime.now()
                now = datetime.strftime(now, "%d/%m/%Y %H:%M:%S")

                if len(priceLine)==0:
                    db.insert_new_data(last_price, now, self.id)

                    priceLine.append(last_price)
                    timeLine.append(now)
                else:
                    if priceLine[-1] != last_price:
                        db.insert_new_data(last_price, now, self.id)
                        priceLine.append(last_price)
                        timeLine.append(now)       

                self.driver.refresh()
                time.sleep(10) 

       
            db.commit_and_close()
            title = soup.find("div", class_ = "marketListing-info-header-title").text

        except Exception as ex:
            print(ex)

        finally:
            self.driver.close()
            self.driver.quit()


if __name__ == "__main__":
    scanner = Scanner(log,pas)
    scanner.set_id(346)
    scanner.run(60)



  