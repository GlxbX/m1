from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
import pandas as pd 
from DB import Database 
from secure_data import log, pas
from multiprocessing import Pool


class Scanner:
    def __init__(self,log,pas, item_id,trade = False):

        #подключение базы данных
        self.db = Database()

        #параметры сканера
        self.trade = trade 
        self.log = log 
        self.pas = pas
        self.id = item_id
        self.buy_limit = 99999
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
        self.url = "https://monopoly-one.com/market/thing/{}".format(self.id)

    #получение цены для продажи с учетом комиссии тп и желаемой прибыли
    def get_sell_price(self, buy_price):
        return round(((buy_price/(85-self.wanted_profit_percent))*100),2)

    #скрипт покупки item
    def buy(self,price, b_time):
        #нажать кнопку купить
        self.driver.find_element(By.CLASS_NAME, "button.button-small.button-grass").click()
        time.sleep(1)

        #нажать кнопку подтверждения купить
        self.driver.find_element(By.CLASS_NAME, "btn.btn-small.btn-error").click()
        time.sleep(2)

        #получить подтверждение покупки
        success = False
        if self.driver.find_element(By.CLASS_NAME, "dialog-box-title").text() == "Покупка совершена!":
            success = True

        #обновить страницу
        self.driver.refresh()

        if success == True:
            #получить желаемуе цену продажи
            listed_price = self.get_sell_price(price)

            #записать транзакцию в бд
            self.db.add_new_transaction(self.id, price, b_time, listed_price)

    #скрипт продажи item
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
    def run(self, minutes):
        #подключение к базе данных
        self.db.connect()

        #создание таблицы движения цены item (если не была создана)
        self.db.create_new_item_table(self.id)

        #получение лимита цены закупки
        self.buy_limit = self.db.get_buy_price_limit(self.id)

        #аутентификация
        self.authentificate()

        #запуск
        try:

            last_price = 0 
            ITEM_NAME = self.db.get_item_name_by_id(self.id)

            #подключение к странице item
            self.driver.get(url=self.url)
            time.sleep(5)

            #основной цикл 
            for i in range(minutes*12):

                #получение данных со страницы
                source_data = self.driver.page_source
                soup = bs(source_data, "lxml")

                #получение данных предмета - первого в очереди на продажу
                min_listing_id, min_listing_price = self.db.get_min_listing_price(self.id)
                
                #текущая цена
                curr_price = soup.find("div", class_ = "marketThing-price")

                #цикл на случай неполадок (временно, позже ожидания будут убраны)
                while curr_price == None:
                    print("Error")
                    self.driver.refresh()
                    time.sleep(5)
                    source_data = self.driver.page_source
                    soup = bs(source_data, "lxml")
                    curr_price = soup.find("div", class_ = "marketThing-price")

                curr_price = float(curr_price.text[:-3])

                #текущее время
                now = datetime.now()
                now = datetime.strftime(now, "%d/%m/%Y %H:%M:%S")

                #блок торговых операций
                if self.trade == True:

                    #закупка item если цена ниже лимита 
                    if curr_price<self.buy_limit:
                        self.buy(curr_price, now)
                        print("---------------- [{}] +1 Item for {} -------".format(ITEM_NAME, curr_price))
                        time.sleep(2)

                    #продажа item при цене выше лимита
                    if curr_price>min_listing_price:
                        sell_price = min_listing_price

                        #повышение цены продажи при имеющейся возможности
                        if curr_price-min_listing_price>0.01:
                            sell_price = curr_price-0.02
                            #обновление данных транзакции в бд
                            self.db.update_listing_price(min_listing_id, sell_price)

                        #обновление очереди предметов на продажу
                        self.sell(min_listing_id, sell_price)
                        print("---------------- [{}] Listed 1 item for {}".format(ITEM_NAME, sell_price))
                        time.sleep(2)
                          
                #блок сканирования цены
                #первыя итерация       
                if last_price == 0:
                    last_price = curr_price

                else:   
                    #понижение цены
                    if curr_price<last_price:
                        print("---------------- [{}] Price decreased {} --> {}".format(ITEM_NAME,last_price, curr_price))
                        last_price = curr_price

                    #нет изменений  
                    elif curr_price==last_price:
                        last_price = curr_price

                    #повышение цены
                    else:
                        print("---------------- [{}] Price increased {} --> {}".format(ITEM_NAME,last_price, curr_price))

                        #обновление данных в транзакциях о проданых предметах 
                        num_of_sold_items = self.db.update_sold_items(curr_price, self.id)
                        if num_of_sold_items>0:
                                print("---------------- [{}] SOLD {} items for {}".format(ITEM_NAME, num_of_sold_items, curr_price))

                        #добавление информации о цене последней продажи в таблицу движения цены
                        self.db.insert_new_data(last_price, now, self.id)
                        last_price = curr_price
  
                self.driver.refresh()
                time.sleep(10) 
                print("[{}] Scanning.... {}".format(ITEM_NAME,i))

            self.db.commit_and_close()
            title = soup.find("div", class_ = "marketListing-info-header-title").text

        except Exception as ex:
            print(ex, "try_cycle_err")

        finally:
            self.driver.close()
            self.driver.quit()


def just_scan(item_id):
    scanner = Scanner(log, pas, item_id)
    scanner.run(10000)

def scan_and_trade(item_id):
    scanner = Scanner(log, pas, item_id, trade=True)
    scanner.run(100)





if __name__ == "__main__":
    ids = [8,344,345,346]

    p = Pool(processes=4)
    p.map(scan_and_trade, ids)

      
# <span class = formatter>
# <span> Выполнить это действие невозможно из-за установленных лимитов. <span>