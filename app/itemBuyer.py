from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time


class Buyer:

    #скрипт покупки item
    def buy(self,id,price):
        success = False

        item_url = "https://monopoly-one.com/market/thing/{}".format(id)
        # self.driver.execute_script("window.open('');")
        # self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(item_url)

        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'marketThing-price'))
        WebDriverWait(self.driver, 10).until(element_present)
        
        pr = self.driver.find_element(By.CLASS_NAME,"marketThing-price").text[:-3]
        curr_price = float(pr)

        if curr_price<=price:
            #нажать кнопку купить
            self.driver.find_element(By.CLASS_NAME, "button.button-small.button-grass").click()

            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-small.btn-error'))
            WebDriverWait(self.driver, 10).until(element_present)
           
            #нажать кнопку подтверждения купить
            self.driver.find_element(By.CLASS_NAME, "btn.btn-small.btn-error").click()
            time.sleep(1)

            #успех или ошибка
            window_after_buy = EC.presence_of_element_located((By.CLASS_NAME, "dialog-box-title"))
            WebDriverWait(self.driver, 5).until(window_after_buy)

            message = self.driver.find_element(By.CLASS_NAME, "dialog-box-title").text
            print(message)
            if message == "Покупка совершена!":
                success = True
        
            elif message == "Ой!":
                success = False
               
            else:
                print("------------------------------------ Buyer had an unknown error")

        # self.driver.close()
        # self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.get(url=self.url)
        time.sleep(1)
        return success


