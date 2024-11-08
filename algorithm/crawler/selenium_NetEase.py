import re
import parsel
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import prettytable

# 指定 ChromeDriver 的路径
service = Service(executable_path=r'D:\tool\toolkit\chromedriver.exe')

# 使用 Service 创建 WebDriver 实例
driver = webdriver.Chrome(service=service)

url = 'https://music.163.com/#/song?id=4331344'
save_path = r'D:\cache\coding\python\crawler\\'
driver.get(url)
print("0")

# 使用显式等待来等待元素可点击
# try:
#     WebDriverWait(driver, 2).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, '.itm'))
#     )
# except TimeoutException:
#     print("元素未在指定时间内加载完成")

print("1")

driver.switch_to.frame(0)
comment_list = driver.find_elements(By.CSS_SELECTOR, '.itm')

print("2")

for comment in comment_list:
    # user_name, content = comment.find_element(By.CSS_SELECTOR, '.cnt').text.split('：')
    content = comment.find_element(By.CSS_SELECTOR, '.cnt').text
    # zan = comment.find_element(By.CSS_SELECTOR, '.zan').text
    # date = comment.find_element(By.CSS_SELECTOR, '.time').text
    print(content)
