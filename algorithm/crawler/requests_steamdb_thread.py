import requests
import os
import json
from bs4 import BeautifulSoup
import pickle

import concurrent.futures
import queue
import threading
import time

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://steamdb.info/search/?a=app&q=&type=1&category=2",
    "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
    "sec-ch-ua-arch": "\"x86\"",
    "sec-ch-ua-bitness": "\"64\"",
    "sec-ch-ua-full-version": "\"130.0.6723.70\"",
    "sec-ch-ua-full-version-list": "\"Chromium\";v=\"130.0.6723.70\", \"Google Chrome\";v=\"130.0.6723.70\", \"Not?A_Brand\";v=\"99.0.0.0\"",
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
    "cf_clearance": "1Ri_hhpmyoxHNneqaRiSv_f5Cz_2q.wFnQcgb2o.h3I-1730867908-1.2.1.1-5MXbHfJFNYgGk_YsCYi28X.hG1lovgnSwRdDCFPaQ..7kK0ZlMBLxJjsnpwKwrsHjYL1as3xWk3NLjQITdcd2HdAvhBB4cbur9Udi7wyOewtaIiURcEES.xckqXbv0ue9ux5hDRiOGLQqWrcL2CKK0aBgRE274iAQHT6T2bgzHOn_XBMPkABLdb8fCLDtNPBTSJkQ83JwSO4x4HyLDcCiNwDbnU2vbm3y0g9JGXV6LkSicbLs6PjjVspPJLLqYAy_7baH2Nr0ohSnmPm2BcA2wziwO3aVEo1mJyGnUW6v.sEH3Rq5tvTTQtLZw4co1NQCwgvyNCQGsop3TaG9mu6pvH0V4.CXMOii4gdlLEUOLCY77J8Rn2.AQGSVeI5e7nKeY_PU5jWxpPw6vsxlueMmvhZ7QW.7rebG2luSK50.JwOXee8XpDjnGAtUKo5fcej",
    "__cf_bm": "QLIrtannHQ8OYEvX.MwJfkr1vpsSLSWyjSdXyeH4ksU-1730867914-1.0.1.1-ixWBdHxs2zFpXlTDrl7Fbepo9mO6XDNqw.SHtavvHiuPi.OsBkwPPuD2yG4HuCFU7CMN92uJxEQmNK_CA4uGKA"
}
url = "https://steamdb.info/search/"
params = {
    "a": "app",
    "q": "",
    "type": "1",
    "category": "2",
    "all": "1"
}

base_save_path = r'C:\Users\11435\Desktop\clutter\research\data\roommate\game'


# 处理数据前需要获取其id
def get_items_id():
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    html = response.text
    item_id = []

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 提取所有class为"app"的tr标签
    tbody = soup.find('tbody')
    # 检查是否找到了tbody标签
    if tbody:
        # 在tbody内找到所有class为"app"的tr标签
        tr_tags = tbody.find_all('tr', class_="app")

        # 循环遍历所有找到的tr标签
        for tr_tag in tr_tags:
            # 提取每个tr标签的data-appid属性
            if 'data-appid' in tr_tag.attrs:
                data_appid = tr_tag['data-appid']
                item_id.append(data_appid)
            else:
                print(f"某个tr标签没有data-appid属性")

    # 将列表存储到pickle文件
    with open('\\'.join([base_save_path, 'item_id.json']), 'wb') as f:
        json.dump(item_id, f)


# 开始多线程处理数据
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


def consumer():
    while True:
        item_html = task_queue.get()
        if item_html is None:  # 收到停止信号
            break
        try:
            item_soup = BeautifulSoup(item_html, 'html.parser')
            item_info_dict = {}

            # title
            item_info_dict['game_name'] = item_soup.find('h1').get_text(strip=True)

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

            result_queue.put(item_info_dict)  # 将处理后的数据放入结果队列
        except Exception as e:
            print(f"处理错误: {e}")
        finally:
            task_queue.task_done()


def main(item_id_list, consumer_func):
    # 启动消费者线程
    num_consumers = 1  # 消费者线程数量
    consumers = []
    for _ in range(num_consumers):
        thread = threading.Thread(target=consumer_func)
        thread.start()
        consumers.append(thread)

    # 使用ThreadPoolExecutor启动生产者线程
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for item_id in item_id_list:
            executor.submit(producer, item_id)

    # 等待所有任务完成
    task_queue.join()

    # 停止消费者线程
    for _ in consumers:
        task_queue.put(None)  # 发送停止信号
    for consumer in consumers:
        consumer.join()

    # 收集结果
    item_info_dict_list = []
    while not result_queue.empty():
        item_info_dict_list.append(result_queue.get())

    # 保存结果到JSON文件
    with open('item_info_dict_list.json', 'w', encoding='utf-8') as f:
        json.dump(item_info_dict_list, f, ensure_ascii=False, indent=4)


# if __name__ == "__main__":
#     item_id_list = [1, 2, 3, ...]  # 假设这是您的ID列表
#     main(item_id_list)
with open('\\'.join([base_save_path, 'item_id.pkl']), 'rb') as f:
    item_id_list = pickle.load(f)
main(item_id_list[:100], consumer)
