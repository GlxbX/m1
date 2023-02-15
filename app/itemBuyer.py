class Buyer:

    def __init__(self, API):
        self.api = API

    #скрипт покупки item
    def buy(self, session, id,price, acc_tok):
        success = False

        last_item = self.api.get_item_listings(session, id, 1)['data']['things'][0]
       

        thing_id = last_item['thing_id']
        curr_price = last_item['price']

        if curr_price<=price:

            params = {'thing_id':thing_id, 'price': round(100*curr_price), 'access_token': acc_tok}
            response = self.api.buy_item(session, params)

            if response['code'] == 0:
                success = True
        
            else:
                print("------------------------------------ Buyer had an unknown error")
                print(response.text)

        else:
            print("-------------------Didnt even see item ", id, price)

        return success


