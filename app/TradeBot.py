from .DB import BaseDB
from .seleniumDriver import SeleniumDriver
from .requestsFuncs import Requests
from .API import API
from .itemBuyer import Buyer
from .priceAnalyzer import Analyzer
from .timeManager import TimeManager


import time
from datetime import datetime

from .custom_objects import Item, Thing


class TradeBot:
    def __init__(self):
        self.total_time = 0
        self.acc_id = 1

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

        #подключение кастомного таймера
        self.time_handler = TimeManager()

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

    def get_item_from_sellup(self, sellup):
        return Item(sellup['thing_prototype_id'], sellup['title'], sellup['price'],sellup['count'])

    def update_sold_items(self):
        t_count = self.db.get_t_counter(self.acc_id)
        params = {'offset': 0, 'count': 50, 'access_token': self.access_token}    

        data = self.api_handler.get_wallet_history(self.requests_handler.session, params)['data']
        count = data['count']
        transactions = data['transactions']

        total_recieved_money = 0

        

        for i in range(count - t_count):
            tran = transactions[i]
            if tran['type'] == 2 and tran['sum']>0:
                thing_id = tran['additional']['item_id']

                all_id =[i[0] for i in self.db.get_t_ids()]
                print(all_id)
                if thing_id in all_id:
                    res_pr = tran['sum']
                    dt = self.get_current_time()

                    total_recieved_money+=res_pr
                    self.db.update_sold_transactions(thing_id, res_pr, dt)
                    print("SOLD item ",thing_id, ' for ', res_pr)

        self.db.update_t_counter(self.acc_id, count)
        self.balance+=total_recieved_money

    def run(self):
        #подключение к базе данных
        self.db.connect()

        self.selenium_handler.authentificate()

        self.access_token = self.selenium_handler.return_access_token()

        self.requests_handler.update_cookie(self.selenium_handler.driver)

        self.balance = self.api_handler.get_account_balance(
                                                            self.requests_handler.session,
                                                            self.access_token
                                                             )['result']['info']['balance']
        
        self.start_cycle()
    
    def start_cycle(self):
      
       
        last_checked_item = Item(0,0,0,0)
        try:
            while True:
                start = time.time()

                last_50_sellups = self.api_handler.get_last_sellups(self.requests_handler.session, 50)['data']['things']
            
                current_item = self.get_item_from_sellup(last_50_sellups[0])
               
                #блок закупки последненго предмета
                if last_checked_item != current_item:
                    
                    try:
                        current_item.wanted_price = self.db.get_wanted_price(current_item.id)
                        if current_item.price <= current_item.wanted_price and current_item.price <= self.balance/2:

                            if current_item.id not in self.items_stoplist:

                                print("Trying to buy ", current_item.name)
                                print(" ")
                                buyer_response = self.buyer.buy(self.requests_handler.session, current_item, self.access_token)

                                if buyer_response[0]==0:
                                    thing = buyer_response[1]
                                    self.balance -= thing.buy_price
                                    self.db.add_new_transaction(thing)
                                    print("Bought", thing.name, thing.buy_price, "- wanted sell price - ", thing.wanted_sell_price)
                                    print(" ")

                                elif buyer_response[0] == 601:
                                    print("Item was alredy bought before us", current_item.id ,current_item.price)
                                    print(" ")

                                elif buyer_response[0] == -1:
                                    print("Didnt even see item ",current_item.id, current_item.price)
                                    print(" ")
                                
                                elif buyer_response[0] == -2:
                                    print("------------------------------------ Buyer had an unknown error")
                                    print(buyer_response[1])

                    except Exception as ex:
                        print("Exeption while buying an item ", ex )

                    finally:
                        last_checked_item = current_item
                    
                #блок обновления цены в бд для последних 50 предметов
                for ident in range(50):
                    try:
                        item = self.get_item_from_sellup(last_50_sellups[ident])

                        last_recorded_price = self.db.get_last_price(item.id)

                        if item.price != last_recorded_price:
                            item.wanted_price = self.db.get_wanted_price(item.id)
                            now  = self.get_current_time()

                            print(item)
                            if item.wanted_price == -1:
                                self.db.add_new_item(item.id, item.name)
                            else:
                                item.wanted_price = self.Analyzer.update_items_info_wanted_price(item.id)

                            self.db.insert_new_data(item.price, item.qty, now, item.id)


                    except Exception as ex:
                        print("Exception while updating items prices ", ex, ident)

                    finally:
                        pass

                
                if self.time_handler.is_transactions_update_time():
                    print(' ')
                    print('UPDATING SOLD ITEMS')
                    print(" ")
                    self.update_sold_items()


                algtime = round((time.time()-start),2)
               
                if algtime<self.api_handler.call_time:
                    time.sleep(self.api_handler.call_time-algtime)
                self.total_time += (time.time()-start)
                # print('ALGO TIME -- ',(round((time.time()-start),2)))
                
                
        except Exception as ex:
            print(self.total_time, ' --- total time')
            print(ex)
            
        finally:
            print(self.total_time, ' --- total time')
            self.selenium_handler.driver.close()
            self.selenium_handler.driver.quit()
            self.db.commit_and_close()