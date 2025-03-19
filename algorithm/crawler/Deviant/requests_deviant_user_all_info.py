import requests
import os
import re
import json
from bs4 import BeautifulSoup
import pandas as pd
import pickle
from tqdm import tqdm
import time
import numpy as np


def extract_user_info(resp):
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
                data['url'] = li_text_tag.find('a').get('href')
            else:
                data['gender'] = li_text

    # 最后处理profile comments
    pc_liked_list = item_html.find_all('div', class_="_2kMWf _2eSya o0DkH")
    for idx, div in enumerate(pc_liked_list):
        if "Profile Comments" in div.text:
            data['Profile Comments'] = div.find('span').text

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


def extract_art_info(resp):
    json_data = json.loads(resp.text)

    data = {
        'username': json_data['deviation']['author']['username'],
        'deviation_name': json_data['deviation']['title'],
        'published_time': json_data['deviation']['publishedTime'],
        'favourites': json_data['deviation']['stats']['favourites'],
        'comments': json_data['deviation']['stats']['comments'],
        'views': json_data['deviation']['stats']['views'],
        'categories': ','.join([tag['name'] for tag in json_data['deviation']['extended']['tags']]),
        'description': json_data['deviation']['extended']['descriptionText']['excerpt'],
        'img_url': json_data['deviation']['url']
    }

    return data


def requests_proxy(url):
    while True:
        try:
            return requests.get(url, headers=headers, cookies=cookies, proxies=proxies)
        except Exception as e:
            print(f"\n url:{url} error:{e}")


proxies = {
    'http': 'http://127.0.0.1:7890',  # Clash的HTTP代理端口
    'https': 'http://127.0.0.1:7890',  # Clash的HTTPS代理端口
}

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "referer": "https://www.deviantart.com/furry-is-forever/about",
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
    "td": "0:944%3B3:304%3B6:824x561%3B10:739%3B12:779.2000122070312x725.5999755859375%3B49:458"
}
params = {
    "deviationid": "1116029905",
    "username": "plumedharfang",
    "type": "art",
    "include_session": "false",
    "csrf_token": "jlyKBRSjGKuGlvNx.spltgy.HmK09FW8xAlfJkWXT7Z-aP9y343bRTM7K3C32HqJvk8",
    "expand": "deviation.related",
    "preload": "true",
    "current_id": "1116167555",
    "da_minor_version": "20230710",
    "page": "1"
}

base_save_dir = r'C:\Users\11435\Desktop\clutter\data\deviant\user_info_animal'
user_info_csv = 'user_basic_info_animal.csv'

user_page_base_url = "https://www.deviantart.com/"
# 先从csv文件中获取user的name
user_basic_info = pd.read_csv(os.path.join(base_save_dir, user_info_csv))
for idx in range(len(user_basic_info)):
    # 先获取用户基本信息
    username = user_basic_info['username'][idx]
    user_page_url = user_page_base_url + username
    response = requests_proxy(user_page_url)
    user_info_data = extract_user_info(response)

    # 计算page_num，用于gallery翻页
    page_num = int(user_info_data['Deviations'])
    user_gallery_url = "https://www.deviantart.com/" + username + "/gallery"
    response = requests_proxy(user_gallery_url)
    token, art_url = extract_art_url(response)

    # 循环便利url
    headers['referer'] = art_url[0]
    params['username'] = username
    params['deviationid'] = art_url[0].split('-')[-1]
    params['csrf_token'] = token
    params['page'] = str(1)
    user_art_url = "https://www.deviantart.com/_puppy/dadeviation/init"
    response = requests_proxy(user_art_url)
    art_info_data = extract_art_info(response)
    break
