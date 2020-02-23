import pickle
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import json

driver = webdriver.Firefox()
driver.get("https://www.instagram.com/accounts/login/?source=auth_switcher")
time.sleep(1)

credentials = json.load(open('instagram.json', 'r'))
user = driver.find_element_by_name("username")
password = driver.find_element_by_name("password")
user.send_keys(credentials['username'])
password.send_keys(credentials['password'])
password.send_keys(Keys.RETURN)

time.sleep(10)

cookies = driver.get_cookies()

s = requests.Session()
for cookie in cookies:
    print(cookie['name'], cookie['value'])
    s.cookies.set(cookie['name'], cookie['value'])

pickle.dump(s, open("session.dat", "wb"))
