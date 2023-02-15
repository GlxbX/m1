import requests

class Requests:
    def __init__(self):
        self.header1 = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

        self.session = requests.Session()
        self.session.headers.update(self.header1)
    

    def update_cookie(self, driver):
        for cookie in driver.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        
    