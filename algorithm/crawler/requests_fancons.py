import requests
import os
import re
import json
from bs4 import BeautifulSoup
import pickle
from tqdm import tqdm
import time
import numpy as np

import concurrent.futures
import queue
import threading

is_proxy = 1
save_path = r'C:\Users\11435\Desktop\clutter\research\data\roommate\fancons'
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://fancons.com/events/schedule.php?year=2023",
    "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}
cookies = {
    "__cf_bm": "u437kcmg5oLsHT9Ov9DvUXHqx_ycVCBobFKnqfa9bck-1730779550-1.0.1.1-rUmFyy_lvw7Ne2DFwQqNVpoRJLk43iAMg2d0L0whOW1hH5uHY6zWdt6V.4q2_h5rUnan6.QeopIJeExT8S7fZg",
    "cf_clearance": "iZ7Cjvtu4.n1XKUTNSx24SPVcrGlC7x1dzVyZER_.d0-1730779815-1.2.1.1-uTN5TPIrvy5xxFOoVJsi8CqraAbdss8l6x8ELxD_dHOCj63L0ITWt4jPUKZXjkQciLFimD8zROSEGGBzJ_oRQAOKdFn5UJZxGY2.wPoVFZIP4XxMUaVHftqmWe8KzBqTae7zc7468i78NV4b42eZtLakvIIBUe0f2FCA_jWKnjHs6OugYAM8ZY24LIFt8C9VCKoKm0T00f8lfVYV6TtHas9Ur25teP4BiiNqoVkWvaptD1rnU5v8UPfQLq3UFeq9zoq32fWqkhlpG1SkDi8W1iKH2FpfKCelCWB5EW.yaH4Sms_Nl_TBe8p5sFR4MDV10ZbwTSNjMtQirtvlDAWMqyfDNUlJz931P_4hvpD7uZfHD8HjLXMri5.p3S9TxErEnSgqOGqZSh7lU9K1Q9xS4W1iI8gvGICVwveUJpiRzTD8rvu36efUIat5ziQACWUY"
}
proxies = {
    'http': 'http://127.0.0.1:7890',  # Clash的HTTP代理端口
    'https': 'http://127.0.0.1:7890',  # Clash的HTTPS代理端口
}

params = {
    "year": "2022"
}

# 共享队列
task_queue = queue.Queue()
# 结果队列
result_queue = queue.Queue()


def producer(item_id):
    item_url = f'https://steamdb.info/app/{item_id}/info/'
    try:
        item_html = requests.get(item_url, headers=headers, cookies=cookies).text
        task_queue.put(item_html)  # 将获取的HTML放入任务队列
    except requests.RequestException as e:
        print(f"请求错误: {e}, id号: {item_id}, url: {item_url}")


def url_extract(html):
    url_list = []
    item_soup = BeautifulSoup(html, 'html.parser')
    item_info = item_soup.find('tbody')
    item_trs = item_info.find_all('tr')
    for tr in item_trs:
        td = tr.find_all('td')
        url = td[0].find('a')['href']
        url_list.append("https://fancons.com" + url)

    return url_list


url = "https://fancons.com/events/schedule.php"
json_data = {}
for year in tqdm(range(1936, 2031)):
    params['year'] = str(year)

    try:
        while True:
            if is_proxy:
                response = requests.get(url, headers=headers, cookies=cookies, params=params,
                                        proxies=proxies, verify=True)
            else:
                response = requests.get(url, headers=headers, cookies=cookies, params=params)

            break
    except Exception as e:
        print(f"error info {e}")

    try:
        current_url_list = url_extract(response.text)
    except Exception as e:
        print(f"epoch is {year} error info {e}")
        current_url_list = None
    json_data[str(year)] = current_url_list
