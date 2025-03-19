import requests
import os
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pickle
import math
import pandas as pd
from tqdm import tqdm
import time
import numpy as np

from utils.integration import dict_integration
from utils.saver import json_saver

proxies = {
    'http': 'http://127.0.0.1:7890',  # Clash的HTTP代理端口
    'https': 'http://127.0.0.1:7890',  # Clash的HTTPS代理端口
}

cookies = {
    'userinfo': '__4d10bcfd6985b26c4ce5%3B%7B%22username%22%3A%22%22%2C%22uniqueid%22%3A%227ef70437863b1cc565e28b1e6583f327%22%2C%22dvs9-1%22%3A1%2C%22ab%22%3A%22tao-2br-1-a-1%22%7D',
    'td': '0:944%3B3:304%3B6:824x561%3B7:1367%3B10:304%3B12:748.7999877929688x725.5999755859375%3B49:428',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.deviantart.com/gustavo-art-brazil/gallery',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-viewport-height': '742',
    'sec-ch-viewport-width': '706',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

params = {
    'deviationid': '265223487',
    'username': 'gustavo-Art-Brazil',
    'type': 'art',
    'include_session': 'false',
    'csrf_token': 'GyBRhxshYxuraFZl.spmfnx.k1Q9xohK639x8Xj5VTUsP3rcMg1Nb9g9pREzyOHKL8I',
    'expand': 'deviation.related',
    'da_minor_version': '20230710',
    "page": "1"
}


def extract_art_info_by_json(resp):
    json_data = json.loads(resp.text)

    data = {
        'username': json_data['deviation']['author']['username'],
        'deviation_name': json_data['deviation']['title'],
        'published_time': json_data['deviation']['publishedTime'],
        'favourites': json_data['deviation']['stats']['favourites'],
        'comments': json_data['deviation']['stats']['comments'],
        'views': json_data['deviation']['stats']['views'],
        'categories': ','.join([tag['name'] for tag in json_data['deviation']['extended']['tags']])
        if 'tags' in json_data['deviation']['extended'] else "",
        'description': json_data['deviation']['extended']['descriptionText']['excerpt'],
        'img_url': json_data['deviation']['url']
    }

    return data


def extract_art_url(resp):
    # extract img url
    item_html = BeautifulSoup(resp.text, 'html.parser')

    token_script = item_html.find_all('script')[-1].get_text()
    token = token_script.split("window.__CSRF_TOKEN__ = '")[-1].split("'")[0]

    art_works_div = item_html.find('div', attrs={'style': 'margin-left:-4px;margin-top:-4px;margin-bottom:-4px'})
    art_works_url_list = [a.get('href') for a in art_works_div.find_all('a', attrs={'aria-label': True}) if
                          a.find('img')]

    return token, art_works_url_list


# todo:log.txt需要修订一下
art_page_base_url = 'https://www.deviantart.com/{}/gallery'
base_save_dir = r'C:\Users\11435\Desktop\clutter\data\deviant\art_info_animal'
user_info_csv = r'C:\Users\11435\Desktop\clutter\data\deviant\user_info_animal.csv'
log_file_path = r'C:\Users\11435\Desktop\clutter\data\deviant\log.txt'

# idx:上次结束的地方+1,也就是下次开始的地方 step:间距
snapshot = {'idx': 0, 'page_num': 1}
snapshot_path = os.path.join(base_save_dir, 'snapshot.json')
if os.path.exists(snapshot_path):
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        snapshot = json.load(f)
    # snapshot判定修正
    if snapshot['idx'] == -1:
        pass
    if snapshot['page_num'] == -1:
        snapshot['idx'] = snapshot['idx'] + 1
        snapshot['page_num'] = 1
else:
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=4)

pbar = tqdm(desc="Processing")

# 先从csv文件中获取user的name
user_info = pd.read_csv(user_info_csv)
page_nums = math.ceil(user_info[0]['deviations'] / 10)
pbar.total = len(user_info)

# 追加模式文件
art_info_append = os.path.join(base_save_dir, "art_info_animal.csv")
append_file_exists = os.path.exists(art_info_append)
if not append_file_exists:
    fd = os.open(art_info_append, os.O_CREAT | os.O_WRONLY, 0o666)
    os.close(fd)

for idx in range(snapshot['idx'], len(user_info)):
    page_nums = math.ceil(user_info[idx]['deviations'] / 10)
    params['username'] = user_info['username'][idx]
    for page_num in range(snapshot['page_num'], page_nums):
        params['page'] = str(page_num)

        # 先抓取gallery页面，解析token和url*10
        response = requests.get(art_page_base_url.format(params['username']), cookies=cookies,
                                headers=headers,
                                params=params, proxies=proxies)

        token, art_urls = extract_art_url(response)
        params['csrf_token'] = token

        # 遍历art url
        art_info_data_list = []
        for page_num_idx, art_url in enumerate(art_urls):
            # 更新和单个art有关的参数
            headers['referer'] = art_url
            params['deviationid'] = art_url.split('-')[-1]

            response = requests.get(
                'https://www.deviantart.com/_puppy/dadeviation/init',
                params=params,
                cookies=cookies,
                headers=headers,
                proxies=proxies,
            )
            art_info_data = extract_art_info_by_json(response)
            art_info_data['idx'] = idx
            art_info_data['gallery_page_num'] = page_num
            art_info_data['gallery_page_num_idx'] = page_num_idx + 1
            art_info_data_list.append(art_info_data)

        # 将art_info_data_list以追加模式写入
        pd.DataFrame(art_info_data_list).to_csv(art_info_append, mode='a', index=False, header=not append_file_exists)
        # 更新snapshot
        snapshot['page_num'] = page_num + 1 if page_num != page_nums else -1
        json_saver(snapshot, os.path.dirname(snapshot_path), os.path.basename(snapshot_path))

    # 参数更新
    snapshot['idx'] = idx + 1 if idx != len(user_info) else -1
    snapshot['page_num'] = 1
    pbar.n = idx + 1
    pbar.refresh()

pbar.close()
