import re
import parsel
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import prettytable

# 指定 ChromeDriver 的路径
service = Service(executable_path=r'D:\tool\toolkit\chromedriver.exe')

# 使用 Service 创建 WebDriver 实例
driver = webdriver.Chrome(service=service)

url = 'https://music.163.com/#/song?id=4331344'
save_path = r'D:\cache\coding\python\crawler\\'
driver.get(url)

driver.switch_to.frame(0)
comment_list = driver.find_elements(By.CSS_SELECTOR, '.itm')

for comment in comment_list:
    user_name, content = comment.find_element(By.CSS_SELECTOR, '.cnt').text.split('：')
    # zan = comment.find_element(By.CSS_SELECTOR, '.zan').text
    date = comment.find_element(By.CSS_SELECTOR, '.time').text
    print(user_name, content, date)
