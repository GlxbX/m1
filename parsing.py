from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
import pandas as pd 
########
import matplotlib.pyplot as plt
#########



ID = 837

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")

options.add_argument("--disable-blink-features=AutomationControlled")
options.headless = True

s=Service(".chromedriver")
driver = webdriver.Chrome(service=s, options=options)

url = "https://monopoly-one.com/market/thing/{}".format(ID)

try:
    A = {}

    driver.get(url=url)
    time.sleep(5)
    for i in range(120):
        print(i)
        source_data = driver.page_source
        soup = bs(source_data, "lxml")
        last_price = soup.find("div", class_ = "marketThing-price")
        last_price = float(last_price.text[:-3])
        now = datetime.now()
        A[str(now.hour)+":"+str(now.minute)] = last_price
        
        driver.refresh()
        time.sleep(5) 

except Exception as ex:
    print(ex)

finally:
    driver.close()
    driver.quit()

df = pd.DataFrame(A.items(), columns = ['Time', 'Price'])
plt.plot(df['Time'], df['Price'], color='red', marker='o')
plt.title('Green Case Price 5 minutes', fontsize=14)
plt.xlabel('Time', fontsize=14)
plt.ylabel('Price', fontsize=14)
plt.grid(True)
plt.show()