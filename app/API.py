import time

class API:
    def __init__(self, time_handler):
        self.last_sellups_link = "https://monopoly-one.com/api/market.getLastSellups?count={}"
        self.last_item_listings_link = "https://monopoly-one.com/api/market.getListing?thing_prototype_id={}&count={}"
        self.buy_item_link = "https://monopoly-one.com/api/market.buy"
        self.get_balance_link = "https://monopoly-one.com/api/execute.wallet"
        self.get_walle_history_link = "https://monopoly-one.com/api/wallet.getHistory"
        self.refresh_access_token_link = "https://monopoly-one.com/api/auth.refresh"

        self.time_handler = time_handler

        self.c = 0
   

    def get_last_sellups(self, session, count):
        s = session.get(self.last_sellups_link.format(count)).json()
        if s['code'] != 0:
            print(s['code'] ,s)

        self.c+=1
        return s

    def get_item_listings(self, session, i_id, count):
        self.c+=1
        return session.get(self.last_item_listings_link.format(i_id, count)).json()

    def buy_item(self, session, params):
        self.c+=1
        return session.post(self.buy_item_link, params).json()
    
    def get_account_balance(self, session, acc_tok):
        self.c+=1
        params= {'access_token':acc_tok}
        response = session.post(self.get_balance_link, params).json()
        self.time_handler.api_call_delay(1)
        return response

    def get_wallet_history(self, session, params):
        self.c+=1
        response = session.post(self.get_walle_history_link, params).json()
        self.time_handler.api_call_delay(1)
        return response
    
    def refresh_access_token(self, session, refresh_token):
        self.c+=1
        response =session.post(self.refresh_access_token_link, refresh_token)

        if response['code'] != 0:
            print(response)

        new_access_token = response['data']['access_token']
        new_refresh_token = response['data']['refresh_token_token']
        return new_access_token, new_refresh_token   
        
