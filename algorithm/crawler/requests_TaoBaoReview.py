# 本项目只能根据现有关键cookies'_m_h5_tk'进行数据解析,如果需要全方位进行数据抓取,需要对其进行逆向
# 另一种解决方式是通过selenium动态的进行cookies的获取
import requests
import re
import parsel
import os
from urllib.parse import urlparse, parse_qs
from utils.saver import json_saver
import json
import time
import hashlib
import subprocess
import concurrent.futures
import random

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}
cookies = {
    "sgcookie": "E100FfpBRwOZE1vQ5bMJcfAVtvAjeeR9oKxPXF%2FgjSFIkIjASigRWgL8npW1a1N4qkVStF4QrNtUci%2BWeuQkBLrvME2gue5FyWasMASgk%2F9qkSro0GsI5iJM5bCzB1gqb4N0",
    "wk_cookie2": "1faa970499b30a34c963a097632d0f17",
    "wk_unb": "UUphzOfdcXH2sDxlLA%3D%3D",
    "_m_h5_tk": "f91f3321afafcbc12ed41688ba8aad01_1729875343605",
    "_m_h5_tk_enc": "a96ca43d81b6aa3ea9ea5f1c9023851e",
    "x5sec": "7b22733b32223a2239346234373266353637613163386232222c22617365727665723b33223a22307c434c2f7238376747454f335673387a2b2f2f2f2f2f774561447a49794d4459314d7a63794d446b344e6a63374e4443586d65546242513d3d227d",
}
params = {
    "jsv": "2.7.4",
    "appKey": "12574478",
    "t": "1729849603128",
    "sign": "847a2afc523d6cf3337fb576df14cf4c",
    "api": "mtop.alibaba.review.list.for.new.pc.detail",
    "v": "1.0",
    "isSec": "0",
    "ecode": "0",
    "timeout": "20000",
    "ttid": "2022@taobao_litepc_9.17.0",
    "AntiFlood": "true",
    "AntiCreep": "true",
    "dataType": "json",
    "valueType": "string",
    "type": "json",
    "data": "{\"itemId\":\"816200929550\",\"bizCode\":\"ali.china.tmall\",\"channel\":\"pc_detail\",\"pageSize\":20,\"pageNum\":3}"
}
url = "https://h5api.m.taobao.com/h5/mtop.alibaba.review.list.for.new.pc.detail/1.0/"


def get_encrypt_sign_by_hashlib(token, t, appkey, json_data):
    # 通过python代码获取加密后的sign,目前淘宝用的是MD5的加密方式
    sign = token + "&" + str(t) + "&" + appkey + "&" + json_data
    MD5 = hashlib.md5()
    MD5.update(sign.encode('utf-8'))
    sign = MD5.hexdigest()
    return sign


def get_encrypt_sign_by_js(token, t, appkey, json_data):
    # Node.js脚本的路径
    script_path = r'D:\academic\coding\PycahrmProjects\trainingField\algorithm\crawler\encrypt_params_TaoBao_sign.js'

    # 要传递给Node.js脚本的参数列表
    sign = token + "&" + str(t) + "&" + appkey + "&" + json_data
    args = [sign]

    # 构建命令行调用
    command = ['node', script_path] + args

    # 使用subprocess.run()执行命令
    result = subprocess.run(command, capture_output=True, text=True)

    # 获取命令行输出数据
    sign = result.stdout.split('\n')[0]

    return sign


def get_params(pageNum=1):
    # 数据处理,获取sign
    token = cookies['_m_h5_tk'].split('_')[0]
    t = int(time.time() * 1000)
    appKey = params['appKey']
    data = json.loads(params['data'])
    data['pageNum'] = pageNum
    json_data = json.dumps(data, ensure_ascii=False).replace(" ", "")

    sign = get_encrypt_sign_by_js(token, t, appKey, json_data)

    return t, sign, json_data


# 能直接通过修改cookies和params对某一个商品的review进行爬取
def get_review_info(save_path, max_page=1):
    review_infos = []  # 数据存放
    pages = max_page  # 抓取最大页数据
    item_id = json.loads(params['data'])['itemId']
    for page_num in range(pages):
        sleep_time = random.gauss(2, 1)
        time.sleep(sleep_time if sleep_time > 0 else 2)
        t, sign, json_data = get_params(page_num)
        params['t'] = t
        params['sign'] = sign
        params['data'] = json_data

        # 处理数据
        response = requests.get(url, headers=headers, cookies=cookies, params=params)
        raw_data = response.json()

        # 如果存在error message则结束
        if "module" not in raw_data['data']:
            print(f'for url: {url} \t the max page is {page_num + 1} ')
            break

        review_data = raw_data['data']['module']['reviewVOList']
        review_infos = review_infos + [
            {'id': review_info['id'],
             'reviewContent': review_info['reviewWordContent'],
             'reviewDate': review_info['reviewDate'],
             'hasPic': True if 'reviewPicPathList' in review_info else False} for review_info in review_data
        ]

    res = {"review_infos": review_infos,
           "num": len(review_infos)}

    json_saver(res, save_path, item_id)


# 通过get_review_info批量获取数据
def batch_get(url_cookies_file, save_path, max_page=5):
    with open(url_cookies_file, 'r', encoding='utf-8') as file:
        # 加载 JSON 数据
        json_data = json.load(file)

    for i in range(len(json_data)):
        item_url = json_data[i]['url']
        for cookie in json_data[i]['cookies']:
            cookies[cookie['name']] = cookie['value']

        # 对params里的data参数里的id进行修改
        parsed_url = urlparse(item_url)
        query_params = parse_qs(parsed_url.query)
        item_id = query_params['id'][0]
        data = json.loads(params['data'])
        data['itemId'] = item_id
        params['data'] = json.dumps(data, ensure_ascii=False).replace(" ", "")

        # get_review_info(save_path=save_path, max_page=max_page)  # 单线程模式

        # 加入多线程模块
        exe = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        exe.submit(get_review_info, save_path, max_page)


base_save_path = r'C:\Users\11435\Desktop\clutter\research\data\topicModels\TaoBao\smart_phone'
url_cookies = base_save_path + '\\tb_cookies.json'
needed_pages = 5
batch_get(url_cookies, base_save_path, needed_pages)
