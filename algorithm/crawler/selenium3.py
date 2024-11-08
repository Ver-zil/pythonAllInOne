import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# os.environ['PATH'] += os.pathsep + 'D:\tool\toolkit'
# 指定 ChromeDriver 的路径

driver = webdriver.Chrome()
# url = 'https://music.163.com/#/song?id=4331344'
# save_path = r'D:\cache\coding\python\crawler\\'
# driver.get(url)
#
# driver.switch_to.frame(0)
# comment_list = driver.find_elements_by_css_selector('itm')
#
# for li in comment_list:
#     content = li.find_elements_by_css_selector('.cnt').text
#     print(content)
