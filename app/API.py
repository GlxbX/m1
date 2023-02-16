import time

class API:
    def __init__(self):
        self.last_sellups_link = "https://monopoly-one.com/api/market.getLastSellups?count={}"
        self.last_item_listings_link = "https://monopoly-one.com/api/market.getListing?thing_prototype_id={}&count={}"
        self.buy_item_link = "https://monopoly-one.com/api/market.buy"
        self.get_balance_link = "https://monopoly-one.com/api/execute.wallet"

        self.call_time = 3600/1750

        self.counter = 0
        self.start_time = time.time() 

    def update_call_time(self):
        n = time.time() - self.start_time

        if n >= 3600:
            self.start_time = time.time()

        r = 1750 - self.counter
        f = 3600 - n
        curr_call_time = f/r

        if self.call_time < curr_call_time: 
            self.call_time -= (curr_call_time - self.call_time)  

        elif self.call_time > curr_call_time:
            self.call_time+= (self.call_time - curr_call_time)

    def get_last_sellups(self, session, count):

        s = session.get(self.last_sellups_link.format(count)).json()
        self.counter+=1
        if s['code'] != 0:
            print(s)
            print(self.counter)
            print(time.time() - self.start_time)

      
        return s

    def get_item_listings(self, session, i_id, count):
        self.counter+=1
        self.update_call_time()
        return session.get(self.last_item_listings_link.format(i_id, count)).json()

    def buy_item(self, session, params):
        self.counter+=1
        self.update_call_time()
        return session.post(self.buy_item_link, params).json()
    
    def get_account_balance(self, session, acc_tok):
        self.counter+=1
        params= {'access_token':acc_tok}
        return session.post(self.get_balance_link, params).json()

    
                
        
