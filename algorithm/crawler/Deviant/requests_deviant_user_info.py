import requests
import os
import re
import json
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import pickle
from tqdm import tqdm
import time
import numpy as np

proxies = {
    'http': 'http://127.0.0.1:7890',  # Clash的HTTP代理端口
    'https': 'http://127.0.0.1:7890',  # Clash的HTTPS代理端口
}

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "referer": "https://www.deviantart.com/animal-art-community/about",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-viewport-height": "776",
    "sec-ch-viewport-width": "435",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
cookies = {
    "userinfo": "__4d10bcfd6985b26c4ce5%3B%7B%22username%22%3A%22%22%2C%22uniqueid%22%3A%227ef70437863b1cc565e28b1e6583f327%22%2C%22dvs9-1%22%3A1%2C%22ab%22%3A%22tao-2br-1-a-1%22%7D",
    "td": "3:304%3B10:304%3B12:418x759%3B40:534%3B48:866%3B49:428"
}
params = {
    'username': 'erizoinfernal',
    'da_minor_version': '20230710',
    'csrf_token': 'I6aX-JrLsoX6gH1w.spmc7g.HAmQTGKbFbqmftS_9qQV5fEuy3RYCl73TdxmqaGQ5TU',
}


def extract_user_info_by_original_page(resp):
    data = {}
    item_html = BeautifulSoup(resp.text, 'html.parser')

    # 提取头部信息
    item_head = item_html.find('div', class_="kqP8O")
    data['username'] = item_head.find('h1', class_="_18oAH").get_text()
    data['description'] = item_head.find('div', class_="_288hv").get_text()

    item_head_detail_span = item_head.find('div', class_="_3jKPw").find_all('span', recursive=False)
    for span_info in item_head_detail_span:
        # 提取value，即第一个span标签内的文本
        value = span_info.find(True).text
        # 提取key，即value之后的文本
        key = span_info.text.strip().replace(value, '').strip()
        data[key] = value

    # 提取体部信息
    item_body = item_html.find('div', class_="_2vziw ds-surface-secondary")

    d_type = item_body.find('div', class_="_13KHC _9pf4k")
    data['type'] = d_type.get_text() if d_type is not None else None

    user_info_list = item_body.find('ul', class_="_3rpUj").find_all('li')
    for idx, li in enumerate(user_info_list):
        li_text_tag = li.find('span', class_="_2cHeo")
        li_text = li_text_tag.text if li_text_tag is not None else None

        if idx == 0:
            data['birth'] = li_text
        elif idx == 1:
            data['location'] = li_text
        elif idx == 2:
            data['experience'] = li_text
        else:
            # 判断tag里是否有url
            if li_text_tag is not None and li_text_tag.find('a') is not None:
                data['unknown_url'] = li_text_tag.find('a').get('href')
            else:
                data['gender'] = li_text

    # 最后处理profile comments
    pc_liked_list = item_html.find_all('div', class_="_2kMWf _2eSya o0DkH")
    for idx, div in enumerate(pc_liked_list):
        if "Profile Comments" in div.text:
            data['Profile Comments'] = div.find('span').text

    return data


def extract_user_info_by_json(resp):
    json_data = json.loads(resp.text)
    data = json_data['pageExtraData']['stats']

    # todo:username换掉,条件判断修改
    for module in json_data['gruser']['page']['modules']:
        if 'about' in module['moduleData'] and \
                'username' in module['moduleData']['about'] and \
                module['moduleData']['about']['username'].lower() == params['username'].lower():
            # 提取信息
            user_info = module['moduleData']['about']
            data['username'] = user_info['username']
            data['country'] = user_info['country']
            data['deviantFor'] = str(datetime.now() - timedelta(seconds=user_info['deviantFor']))
            data['type-isArtist'] = user_info['isArtist']
            data['dobYear'] = user_info['dobYear']
            data['dobMonth'] = user_info['dobMonth']
            data['dobDay'] = user_info['dobDay']
            data['gender'] = user_info['gender']
            data['description'] = user_info['tagline']

    return data


def requests_proxy(url, **proxy_params):
    while True:
        try:
            return requests.get(url, **proxy_params)
        except Exception as e:
            print(f"\n url:{url} error:{e}")


def json_saver(json_data, save_dir, fid):
    with open(os.path.join(save_dir, fid + ".json"), 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)


def log_info(log_path, msg):
    # 打开文件以追加模式写入
    with open(log_path, 'a') as file:
        # 写入错误信息并添加换行符
        file.write(msg + '\n')


user_page_base_url = "https://www.deviantart.com/"
base_save_dir = r'C:\Users\11435\Desktop\clutter\data\deviant\user_info_furry'
user_basic_info_csv = r'C:\Users\11435\Desktop\clutter\data\deviant\user_basic_info_furry.csv'
log_file_path = r'C:\Users\11435\Desktop\clutter\data\deviant\log_furry.txt'

# idx:上次结束的地方+1,也就是下次开始的地方 step:间距
snapshot = {'idx': 0, 'step': 10}
snapshot_path = os.path.join(base_save_dir, 'snapshot.json')
if os.path.exists(snapshot_path):
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        snapshot = json.load(f)
else:
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=4)

pbar = tqdm(desc="Processing")

# 先从csv文件中获取user的name
user_basic_info = pd.read_csv(user_basic_info_csv)
pbar.total = len(user_basic_info)

user_info_data_list = []
for idx in range(snapshot['idx'], len(user_basic_info)):
    # 先获取用户基本信息
    username = user_basic_info['username'][idx].lower()
    user_page_url = user_page_base_url + username

    response = requests_proxy(user_page_url, headers=headers, cookies=cookies, proxies=proxies)

    item_html = BeautifulSoup(response.text, 'html.parser')
    token_script = item_html.find_all('script')[-1].get_text()
    token = token_script.split("window.__CSRF_TOKEN__ = '")[-1].split("'")[0]

    params['csrf_token'] = token
    params['username'] = username

    response = requests_proxy(
        'https://www.deviantart.com/_puppy/dauserprofile/init/about',
        params=params,
        cookies=cookies,
        headers=headers,
        proxies=proxies,
    )

    if response.status_code != 200:
        log_info(log_file_path,
                 msg=f"this user may not exists\t username:{username}\t idx:{idx + 1}")
        continue

    # todo:exception header的refer最好看一下
    user_info_data = extract_user_info_by_json(response)

    user_info_data_list.append(user_info_data)

    if (idx + 1) % snapshot['step'] == 0 or idx == len(user_basic_info):
        json_saver(user_info_data_list, base_save_dir, str(idx + 1))
        user_info_data_list = []

        snapshot['idx'] = idx + 1
        json_saver(snapshot, base_save_dir, 'snapshot')

    pbar.n = idx + 1
    pbar.refresh()

pbar.close()
