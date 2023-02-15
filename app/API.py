import time

class API:
    def __init__(self):
        self.last_sellups_link = "https://monopoly-one.com/api/market.getLastSellups?count={}"
        self.last_item_listings_link = "https://monopoly-one.com/api/market.getListing?thing_prototype_id={}&count={}"
        self.buy_item_link = "https://monopoly-one.com/api/market.buy"
        self.c = 0
        self.st = 0

    def get_last_sellups(self, session, count):

        s = session.get(self.last_sellups_link.format(count)).json()
        self.c+=1
        if self.c == 1:
            self.st = time.time()

        if s['code'] != 0:
            print(s)
            print(self.c)
            print(time.time() - self.st)
        return s

    def get_item_listings(self, session, i_id, count):
        return session.get(self.last_item_listings_link.format(i_id, count)).json()

    def buy_item(self, session, params):
        return session.post(self.buy_item_link, params)

    
                
        
