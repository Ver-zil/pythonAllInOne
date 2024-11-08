# 利用selenium收集cookies信息

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import time
from urllib.parse import urlparse, parse_qs
from utils.reader import txt_line_reader
from utils.saver import json_saver
from utils.converter import timestamp2time

urls_file = r'C:\Users\11435\Desktop\clutter\research\data\topicModels\TaoBao\smart_phone\url_list.txt'  # 指定url文件
# ["sgcookie", "wk_cookie2", "wk_unb", "_m_h5_tk", "_m_h5_tk_enc", "x5sec"]
cookies_args = []  # 需要从cookies里提取的参数
save_dir = r'C:\Users\11435\Desktop\clutter\research\data\roommate\game'
fid = 'cookies'
login_needed = False  # 登录来保存最开始的cookies参数
base_url = 'https://tb.alicdn.com/'  # 登录用的url

options = Options()
options.add_argument(r"--user-data-dir=C:\Users\11435\AppData\Local\Google\Chrome\User Data")  # 指定用户数据目录
# options.add_argument(r"--user-data-dir=C:\Users\11435\Desktop\clutter\cache\python\chrome")  # 该数据目录专门给收集cookies时使用
options.add_argument("--no-sandbox")
options.add_argument('--disable-dev-shm-usage')

# 指定 ChromeDriver 的路径
service = Service(executable_path=r'D:\tool\toolkit\driver\chromedriver.exe')

# 使用 Service 创建 WebDriver 实例
driver = webdriver.Chrome(service=service, options=options)
if login_needed:
    driver.get(base_url)
    time.sleep(10)

# url_list = txt_line_reader(urls_file)
url_list = ['https://steamdb.info/app/50/']
url_list = [url for url in url_list if url != '']
cookies_infos = []
for i in range(len(url_list)):
    url = url_list[i]
    driver.get(url)
    time.sleep(3)

    # driver.refresh()
    # parsed_url = urlparse(url)
    # query_params = parse_qs(parsed_url.query)
    cookies = driver.get_cookies()
    cookies_info = {'url': url}
    if cookies_args:
        for cookie in cookies:
            cookie.update({"time": timestamp2time(cookie["expiry"]) if cookie["expiry"] else None})
        cookies_info['cookies'] = [cookie for cookie in cookies if cookie['name'] in cookies_args]

    else:
        for cookie in cookies:
            cookie.update({"time": timestamp2time(cookie["expiry"]) if cookie["expiry"] else None})
        cookies_info['cookies'] = [cookie for cookie in cookies]

    cookies_infos.append(cookies_info)

json_saver(cookies_infos, save_dir, fid)
