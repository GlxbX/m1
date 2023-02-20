from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from .secure_data import log, pas

class SeleniumDriver:
    def __init__(self, time_handler):
        # настройки webdriver
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--disable-software-rasterizer")
        self.options.add_argument("--disable-gpu")
        self.options.add_experimental_option("excludeSwitches", ['enable-logging'])
        self.options.headless = False
        self.service = Service("C:\cdriver\chromedriver")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

        self.time_handler = time_handler

    def return_access_token(self):
        return self.driver.execute_script("return localStorage.getItem('access_token')")


    #аутентификация

    #######
    #ДОРАБОТАТЬ с использование EC
    #######
    def authentificate(self):
        #страница аутентификациИ
        self.driver.get(url='https://monopoly-one.com/auth')
        time.sleep(5)

        #логгин
        log_input = self.driver.find_element(By.ID, "auth-form-email")
        log_input.clear()
        log_input.send_keys(log)
        self.time_handler.api_call_delay(1)

        #пароль
        pas_input = self.driver.find_element(By.ID, "auth-form-password")
        pas_input.clear()
        pas_input.send_keys(pas)
        self.time_handler.api_call_delay(1)

        #кнопка submit
        login_button = self.driver.find_element(By.CLASS_NAME  , "btn-ok").click()
        self.time_handler.api_call_delay(1)
        



