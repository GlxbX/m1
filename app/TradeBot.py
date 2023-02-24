from .DB import BaseDB
from .seleniumDriver import SeleniumDriver
from .requestsFuncs import Requests
from .API import API
from .itemBuyer import Buyer
from .priceAnalyzer import Analyzer
from .timeManager import TimeManager


import time


from .custom_objects import Item


class TradeBot:
    def __init__(self):
        self.acc_id = 1

        #подключение базы данных
        self.db = BaseDB()

        #подключение кастомного таймера
        self.time_handler = TimeManager()

        #подключение драйвера
        self.selenium_handler = SeleniumDriver(self.time_handler)

        #подключение request
        self.requests_handler = Requests()

        #подлючение API
        self.api_handler = API(self.time_handler) 

        #подключение закупщика
        self.buyer = Buyer(self.api_handler,self.time_handler)

        #подключение анализатора
        self.Analyzer = Analyzer(self.db, self.time_handler)

        #переменные 
        self.balance = 2.83
        self.access_token = None
        self.refresh_token = None 

        #Stoplist закупки
        self.items_stoplist = [923,935 ,985, 984, 942, 852, 554, 823, 556, 945, 558, 559, 564, 82, 199, 45, 73, 86, 46, 48, 105, 111, 97, 96, 208, 263, 390]



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
            value = tran['sum']
            type = tran['type']
            timestamp = tran['ts']

            if value>0:
                #продажа на маркете или в систему
                if type == 2 or type == 3:

                    thing_id = tran['additional']['item_id']
                    stored_ids =[i[0] for i in self.db.get_t_ids()]
                    
                    if thing_id in stored_ids:
                    
                        dt = self.time_handler.get_datetime_from_timestamp(timestamp)

                        self.db.update_sold_transactions(thing_id, value, dt)

                        print("SOLD item ",thing_id, ' for ', value)
                        print(" ")

                    total_recieved_money+=value 
                
        print("Total recieved money - ", total_recieved_money)
        print("-------------------")
        print(" ")
        self.db.update_t_counter(self.acc_id, count)
        self.balance+=total_recieved_money

    def run(self):
        #подключение к базе данных
        self.db.connect()

        self.selenium_handler.authentificate()

        self.access_token = self.selenium_handler.return_access_token()

        self.refresh_token = self.selenium_handler.return_refresh_token()

        self.requests_handler.update_cookie(self.selenium_handler.driver)

        self.update_sold_items()

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

                #API call for sellups 
                last_50_sellups = self.api_handler.get_last_sellups(self.requests_handler.session, 50)['data']['things']
            
                current_item = self.get_item_from_sellup(last_50_sellups[0])
               
                #блок закупки последненго предмета
                if last_checked_item != current_item:
          
                    try:
                        current_item.wanted_price = self.db.get_wanted_price(current_item.id)
                        print(current_item)
                        print(" ")
                        if current_item.price <= current_item.wanted_price and current_item.price <= self.balance/3:

                            if current_item.id not in self.items_stoplist:
                                print("---------")
                                print("Trying to buy ", current_item.name)
                                print(" ")
                                buyer_response = self.buyer.buy(self.requests_handler.session, current_item, self.access_token)

                                if buyer_response[0]==0:
                                    thing = buyer_response[1]
                                    self.balance -= thing.buy_price
                                    self.db.add_new_transaction(thing)
                                    print("Bought", thing.name, thing.buy_price, "- wanted sell price - ", thing.wanted_sell_price)
                                    print(" ")
                                    print("---------")

                                elif buyer_response[0] == 601:
                                    print("Item was alredy bought before us", current_item.id ,current_item.price)
                                    print(" ")
                                    print("---------")

                                elif buyer_response[0] == -1:
                                    print("Didnt even see item ",current_item.id, current_item.price)
                                    print(" ")
                                    print("---------")
                                
                                elif buyer_response[0] == -2:
                                    print("------------------------------------ Buyer had an unknown error")
                                    print(buyer_response[1])

                        elif current_item.price <= current_item.wanted_price and current_item.price < self.balance/2:
                            print("Not enought money to buy  ", current_item)
                            print(" ")


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
                            now  = self.time_handler.get_current_time()

                            
                            if item.wanted_price == -1:
                                self.db.add_new_item(item.id, item.name)
                            else:
                                item.wanted_price = self.Analyzer.update_items_info_wanted_price(item.id)

                            self.db.insert_new_data(item.price, item.qty, now, item.id)


                    except Exception as ex:
                        print("Exception while updating items prices ", ex, ident)

                    finally:
                        pass
                
                #обновление данных о проданных предметах
                if self.time_handler.is_transactions_update_time():
                    try:
                        print("-------------------")
                        print('UPDATING SOLD ITEMS')
                        print(" ")
                        self.update_sold_items()

                    except Exception as Ex:
                        print("Error while updating sold items", Ex)
                    
                    finally:
                        pass

                #Отчет
                if self.time_handler.is_report_time():
                    try:
                        print("------ 15 minutes report ------")
                        print("Total API cals = ", self.api_handler.c)
                        print(" ")
                        print("Total time = ", time.time() - self.time_handler.TOTAL_TIME_START)
                        print(" ")
                        print("AVG api calltime = ",(time.time() - self.time_handler.TOTAL_TIME_START)/self.api_handler.c)
                        print(" ")
                        print("Current balance = ", self.balance)
                        print("-----------------------------")

                    except Exception as Ex:
                        print("Error while creating report", Ex)

                    finally:
                        pass 

                #Обновление acces токена
                if self.time_handler.is_update_token_time():
                    try:
                        acc_tok, ref_tok = self.api_handler.refresh_access_token(self.requests_handler.session, self.refresh_token)
                    
                    except Exception as Ex:
                        print("Error while refreshing access token ", Ex)
                    
                    finally:
                        self.access_token, self.refresh_token = acc_tok, ref_tok

                

                self.time_handler.main_cycle_delay((time.time()-start))
        
        except Exception as ex:
            print("Error in main cycle" ,ex)
            
        finally:
            print(time.time() - self.time_handler.TOTAL_TIME_START, ' --- total time')
            self.selenium_handler.driver.close()
            self.selenium_handler.driver.quit()
            self.db.commit_and_close()