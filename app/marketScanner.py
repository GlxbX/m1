from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime



class Scanner:
    def get_current_market_listings(self):
        source_data = self.driver.page_source
        soup = bs(source_data, "lxml")
        market_listings = soup.find("a", class_="list-one marketThing")
        return market_listings

    def get_item_id(self,listing):
        return int(listing.get('href')[14:]) 

    def get_item_qty(self, listing):
        return self.make_float_from_str(listing.find("div", class_="marketThing-seller").text[:-4])
    

    def get_item_price(self,listing):
        return self.make_float_from_str(listing.find("div", class_ ="marketThing-price").text[3:-9])

    def get_item_name(self,listing):
        return listing.find("div", class_ = "marketThing-info-title").text

    # def get_listing_params(self,listing):
    #     item_id = int(listing.get('href')[14:]) 
    #     qty = self.make_float_from_str(listing.find("div", class_="marketThing-seller").text[:-4])
    #     price = self.make_float_from_str(listing.find("div", class_ ="marketThing-price").text[3:-9])
    #     item_name = listing.find("div", class_ = "marketThing-info-title").text
    #     return item_id, qty, price, item_name

    def make_float_from_str(self,pr:str):
        l = pr.replace('\u2009', '')
        a = l
        return float(a)

    def get_current_time(self):
        now = datetime.now()
        now = datetime.strftime(now, "%d/%m/%Y %H:%M:%S")
        return now

    

        