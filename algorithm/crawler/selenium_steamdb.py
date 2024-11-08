from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pickle
import time

options = Options()
# options.add_argument(r"--user-data-dir=C:\Users\11435\AppData\Local\Google\Chrome\User Data")  # 指定用户数据目录
options.add_argument(r"--user-data-dir=C:\Users\11435\Desktop\clutter\cache\python\chrome")  # 该数据目录专门给收集cookies时使用
options.add_argument("--no-sandbox")
options.add_argument('--disable-dev-shm-usage')

# 指定 ChromeDriver 的路径
service = Service(executable_path=r'D:\tool\toolkit\driver\chromedriver.exe')

# 使用 Service 创建 WebDriver 实例
driver = webdriver.Chrome(service=service, options=options)

base_save_path = r'C:\Users\11435\Desktop\clutter\research\data\roommate\game'
with open('\\'.join([base_save_path, 'item_id.pkl']), 'rb') as f:
    item_id_lists = pickle.load(f)

for i in range(5):
    url = f'https://steamdb.info/app/{item_id_lists[i]}/'

    driver.get(url)

    time.sleep(1)

iframe = driver.find_elements(By.CSS_SELECTOR, '#cf-chl-widget-za1v5')
driver.switch_to.frame(0)
comment_list = driver.find_elements(By.CSS_SELECTOR, '#cf-chl-widget-za1v5')