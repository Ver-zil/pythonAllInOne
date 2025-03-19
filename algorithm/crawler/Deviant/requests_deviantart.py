import requests
import os
import re
import json
from bs4 import BeautifulSoup
import pickle
from tqdm import tqdm
import time
import numpy as np


def json_saver(json_data, save_dir, fid):
    with open(os.path.join(save_dir, fid + ".json"), 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)


snapshot = {}
base_save_dir = r'C:\Users\11435\Desktop\clutter\data\deviant\user_info_animal'
pbar = tqdm(desc="Processing")
pbar.total = 12600

# 制作snapshot系统，每次中断以后可以从snapshot.json中恢复上次的状态
# 先判断snapshot文件是否存在，如果存在直接读取
snapshot_file_path = os.path.join(base_save_dir, "snapshot.json")
if os.path.exists(snapshot_file_path):
    with open(snapshot_file_path, 'r', encoding='utf-8') as f:
        snapshot = json.load(f)
else:
    # 手动初始化snapshot系统
    snapshot['start'] = "15"
    snapshot['limit'] = "24"
    snapshot['next_offset'] = "15"
    json_saver(snapshot, base_save_dir, "snapshot")

proxies = {
    'http': 'http://127.0.0.1:7890',  # Clash的HTTP代理端口
    'https': 'http://127.0.0.1:7890',  # Clash的HTTPS代理端口
}

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "priority": "u=1, i",
    "referer": "https://www.deviantart.com/animal-art-community/about",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-viewport-height": "776",
    "sec-ch-viewport-width": "743",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
cookies = {
    "userinfo": "__4d10bcfd6985b26c4ce5%3B%7B%22username%22%3A%22%22%2C%22uniqueid%22%3A%227ef70437863b1cc565e28b1e6583f327%22%2C%22dvs9-1%22%3A1%2C%22ab%22%3A%22tao-2br-1-a-1%22%7D",
    "td": "12:726.4000244140625x759.2000122070312%3B48:866"
}
url = "https://www.deviantart.com/_puppy/gruser/module/watchers"
params = {
    "gruserid": "12344814",
    "gruser_typeid": "4",
    "username": "Animal-Art-Community",
    "moduleid": "5966062619",
    "offset": "15",
    "limit": "24",
    "da_minor_version": "20230710",
    "csrf_token": "bEkXh8CLU4_9srp8.spinb7.TZRzezA60W6x40N7M75Zstz-PHR14pENd3s9lr5QajU"
}


def extract_data(response):
    json_data = json.loads(response.text)

    snapshot['next_offset'] = str(json_data['nextOffset'])
    user_info = json_data['results']

    json_saver(user_info, base_save_dir, params['offset'])


for i in range(2):
    # snapshot特化
    params['offset'] = snapshot['next_offset']
    while True:
        try:
            response = requests.get(url, headers=headers, cookies=cookies, params=params, proxies=proxies)
            break
        except Exception as e:
            print(f"error: {e}")
            time.sleep(3)

    # 提取数据，并且最后保存snapshot
    extract_data(response)
    json_saver(snapshot, base_save_dir, "snapshot")
    pbar.n = int(params['offset'])
    pbar.refresh()

pbar.close()
