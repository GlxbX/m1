from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time


class Buyer:

    #скрипт покупки item
    def buy(self,id,price):
        
        success = False

        listing_url = "https://monopoly-one.com/api/market.getListing?thing_prototype_id={}&count=1".format(id)

        for cookie in self.driver.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

        sess = self.session.get(listing_url)
        last = sess.json()
        last_item = last['data']['things'][0]

        thing_id = last_item['thing_id']
        curr_price = last_item['price']

        
        
        acc_tok = self.driver.execute_script("return localStorage.getItem('access_token')")


        if curr_price<=price:
            params = {'thing_id':thing_id, 'price': round(100*curr_price), 'access_token': acc_tok}
            url = "https://monopoly-one.com/api/market.buy"
            resp = self.session.post(url, params)


            if resp.json()['code'] == 0:
                success = True
        
            else:
                print("------------------------------------ Buyer had an unknown error")
                print(resp.text)

           

        self.driver.refresh()
    
        return success


