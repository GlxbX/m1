from .DB import BaseDB
from .seleniumDriver import SeleniumDriver
from .requestsFuncs import Requests
from .API import API
from .itemBuyer import Buyer
from .priceAnalyzer import Analyzer
import time
from datetime import datetime

class TradeBot:
    def __init__(self):
        #подключение базы данных
        self.db = BaseDB()

        #подключение драйвера
        self.selenium_handler = SeleniumDriver()

        #подключение request
        self.requests_handler = Requests()

        #подлючение API
        self.api_handler = API() 

        #подключение закупщика
        self.buyer = Buyer(self.api_handler)

        #подключение анализатора
        self.Analyzer = Analyzer(self.db)

        #переменные 
        ###########
        #Добавить в бд таблицу аакаунта с полем баланс 
        #для отслеживания баланса без парсинга
        ###########
        self.balance = 2.83
        self.access_token = None


        #Stoplist закупки
        self.items_stoplist = [935 ,985, 984, 942, 852, 554, 823, 556, 945, 558, 559, 564, 82, 199, 45, 73, 86, 46, 48, 105, 111, 97, 96, 208, 263, 390]

    def get_current_time(self):
        now = datetime.now()
        now = datetime.strftime(now, "%d/%m/%Y %H:%M:%S")
        return now

    def run(self):
        #подключение к базе данных
        self.db.connect()

        self.selenium_handler.authentificate()

        self.access_token = self.selenium_handler.return_access_token()

        self.requests_handler.update_cookie(self.selenium_handler.driver)

        self.start_cycle()
    
    def start_cycle(self):
      
       
        last_checked_item = [0,0]
        try:
            while True:
                start = time.time()

                last_50_sellups = self.api_handler.get_last_sellups(self.requests_handler.session, 50)['data']['things']
                
                last_item = last_50_sellups[0]
           
                #Получаем id и цену
                item_name = last_item['title']
                item_id = last_item['thing_prototype_id']
                price = last_item['price']
            
                current_item = [item_id, price]
            

                if last_checked_item != current_item:

                    wanted_price = self.db.get_wanted_price(item_id)
                    if price <= wanted_price and price <= self.balance:

                        if item_id not in self.items_stoplist:

                            print("Trying to buy ", item_name)
                            try_to_buy = self.buyer.buy(self.requests_handler.session, item_id, price, self.access_token)

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
                            wanted_price = self.Analyzer.update_items_info_wanted_price(item_id)

                        print("{} current price is {} - want {}".format(item_name, price, wanted_price))
                        print("")
                            

                        self.db.insert_new_data(price, qty, now, item_id)
                   
                last_checked_item = current_item


                for ident in range(1,50):
                    item = last_50_sellups[ident]

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
                            wanted_price = self.Analyzer.update_items_info_wanted_price(item_id)

                        self.db.insert_new_data(price, qty, now, item_id)

                algtime = round((time.time()-start),2)
               
                if algtime<2.1:
                    time.sleep(2.1-algtime)
                # print('ALGO TIME -- ',(round((time.time()-start),2)))
                
                
        except Exception as ex:
            print()
            print(ex)

        finally:
            self.selenium_handler.driver.close()
            self.selenium_handler.driver.quit()
            self.db.commit_and_close()