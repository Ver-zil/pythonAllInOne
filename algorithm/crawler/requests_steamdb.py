import requests
import os
import re
import json
from bs4 import BeautifulSoup
import pickle
from tqdm import tqdm
import time
import numpy as np

is_proxy = 1
init_stpt = 37000
base_save_path = r'C:\Users\11435\Desktop\clutter\research\data\roommate\game2'
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://steamdb.info/",
    "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
    "sec-ch-ua-arch": "\"x86\"",
    "sec-ch-ua-bitness": "\"64\"",
    "sec-ch-ua-full-version": "\"130.0.6723.92\"",
    "sec-ch-ua-full-version-list": "\"Chromium\";v=\"130.0.6723.92\", \"Google Chrome\";v=\"130.0.6723.92\", \"Not?A_Brand\";v=\"99.0.0.0\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "\"\"",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-ua-platform-version": "\"15.0.0\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}
cookies = {
    "__cf_bm": "lNMOPbrujV_Y3poREPj7iye9mWFl8qnqALQWgQZtmMI-1731305234-1.0.1.1-sw8RDjXPYQeMP7dQSuFQbvh4kuvFc9uYYk96.RwNOw26oGm7.Ih2YPmIEUvMZDkZ6WXPZIS4MjxXG7HuBRMmIA",
    "cf_clearance": "y6f2.m8hL5kHYszXBNPH.a4EqShxXTGrb0qR.UwRD48-1731305846-1.2.1.1-jQ1uqeK6oWvYcjyrrGcUsjGe.XiGt8abjD.C6lx5xFa_iLf43jXDFnP8jLNGQfl21UKZP8slESPTwTZlgpU3rMgYQgvImz6bm3OmxwUfb.ofv.5C3WNX94Huqw.AuKcEQ76SiCCRO9ahB1fojciuzK3Cro2JoM9zEBEmaF1eeo2C2JhrXPIde2gSeVWUthQEOAQfB2dYFl6Viu7.bf.vUnnBZV3dpomYaWfevS.FtYuQ7nvamLUYGjNVi8vd632qqkCDlD6gU7IomPTso1RT_.IMyfyb_CKcLJ7USsUYRw9IaNQU8JerzFkz2XpvzYhyVw7u8TXRrEjKBGwdExu0R4bxzjR3i.Y1X_DbBCxMSjHqqqmUrNNpJwdDJ2g3LfGqvHvUtRpuBgDCgLdSM4NPhaHPIlPWToG2zZhf19LFLdE"
}
strategy = {
    'package_interval': 3,
    'group_interval': 5,
    'round_interval': 12
}

proxies = {
    'http': 'http://127.0.0.1:7890',  # Clash的HTTP代理端口
    'https': 'http://127.0.0.1:7890',  # Clash的HTTPS代理端口
}

model = 1


def get_item_infos(item_id_list, idx_start):
    item_info_dict_list = []
    pbar = tqdm(total=len(item_id_list))
    for idx, id in enumerate(item_id_list):

        # 处理某些被删除的值 ['551']
        # if id in ["551"]:
        #     continue

        item_url = f'https://steamdb.info/app/{id}/info/'

        if idx % model == 0:
            if is_proxy:
                while True:
                    try:
                        item_html = requests.get(item_url, headers=headers, cookies=cookies,
                                                 proxies=proxies, verify=True).text
                        break
                    except Exception as e:
                        print(e)
            else:
                item_html = requests.get(item_url, headers=headers, cookies=cookies).text
        else:
            item_html = requests.get(item_url, headers=headers, cookies=cookies, verify=True, proxies=proxies).text
        item_soup = BeautifulSoup(item_html, 'html.parser')

        try:
            # title
            item_info_dict = {'idx': idx_start + idx, 'game_name': item_soup.find('h1').get_text(strip=True)}

            # infos
            item_info = item_soup.find('tbody')
            item_trs = item_info.find_all('tr')
            for tr in item_trs:
                td = tr.find_all('td')
                key = td[0].get_text(strip=True)
                value = td[1].get_text(strip=True)
                item_info_dict[key] = value

            # metadata
            meta = item_soup.find('h2', string='Additional Information').find_next('table')
            meta_trs = meta.find('tbody').find_all('tr', recursive=False)
            for tr in meta_trs:
                td = tr.find_all('td')
                key = td[0].get_text(strip=True)
                value = td[1].get_text(strip=True)
                item_info_dict[key] = value

            item_info_dict_list.append(item_info_dict)
            pbar.update(1)

        except Exception as e:
            print(f'错误信息{e},idx:{idx_start + idx} url:{item_url}')
            return item_info_dict_list

        if idx % 10 == 0:
            time.sleep(10)
        else:
            rd = np.random.normal(loc=strategy['package_interval'], scale=0.5)
            time.sleep(rd if rd > 0 else 0)

    return item_info_dict_list


def get_latest_version(dir, prefix='game_item_info_'):
    max_num = init_stpt

    for file_name in os.listdir(dir):
        if file_name.endswith('.json'):
            match = re.match(prefix + r'(\d+)', file_name)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
    return max_num


def sleep_with_progress_tqdm(duration, interval=1):
    for _ in tqdm(range(int(duration)), desc="Sleeping"):
        time.sleep(interval)


start = get_latest_version(base_save_path)
bkpt = 40000
step = 10
error_list = []
with open('\\'.join([base_save_path, 'item_id.pkl']), 'rb') as f:
    item_id_lists = pickle.load(f)
for i in range(start, len(item_id_lists), step):

    print(f"current epoch : from {i} to {i + step}")
    id_list = item_id_lists[i:i + step]
    data = get_item_infos(id_list, i)

    if len(data) < step:
        # 处理错误，用dp进行验证
        print(f"end bkpt is {i}")
        error_list.append(i)
        break

    file_path = '\\'.join([base_save_path, 'game_item_info_' + str(i + step) + '.json'])
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    if i == bkpt:
        break

    if i % 90 == 0:
        # time.sleep(60)
        sleep_with_progress_tqdm(strategy['round_interval'], 60)
    else:
        time.sleep(strategy['group_interval'])
