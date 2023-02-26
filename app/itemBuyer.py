from .custom_objects import Item, Thing


class Buyer:

    def __init__(self, API, time_handler):
        self.api = API
        self.time_handler = time_handler

    #скрипт покупки item
    def buy(self, session, item, acc_tok):
      
        last_thing = self.api.get_item_listings(session, item.id, 1)['data']['things'][0]
       
        thing_id = last_thing['thing_id']
        buy_price = last_thing['price']

        if buy_price<=item.price:

            params = {'thing_id':thing_id, 'price': round(100*buy_price), 'access_token': acc_tok}
            response = self.api.buy_item(session, params)

            self.time_handler.api_call_delay(2)
            
            if response['code'] == 0:
                
                wanted_sell_price = round(((item.wanted_price*1.1)/85)*100,2)
                thing = Thing(thing_id, item.name, buy_price, wanted_sell_price)
                return [0, thing]

            elif response['code'] == 601:
                return [601, None]
                
            
            else:
                return [-2, response]
                

        else:
            self.time_handler.api_call_delay(1)
            return [-1, None]
           

        


