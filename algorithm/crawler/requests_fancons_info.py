import requests
from bs4 import BeautifulSoup
import json
import html
from utils.reader import json_reader
from utils.saver import json_saver
import concurrent.futures
import queue
from threading import Thread, Lock
from tqdm import tqdm
import time

save_path = r'C:\Users\11435\Desktop\clutter\research\data\roommate\fancons'

stpt = 24500
bkpt = 30000
step = 100

is_proxy = 1
proxies = {
    'http': 'http://127.0.0.1:7890',  # Clash的HTTP代理端口
    'https': 'http://127.0.0.1:7890',  # Clash的HTTPS代理端口
}
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://fancons.com/events/',
    'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
}

lock = Lock()
pbar = None
fancons_url = json_reader(save_path, 'fancons_url')
url_list = [url for v in fancons_url.values() for url in v]


def get_request(url):
    cnt = 0
    fail = 10
    response = None
    while cnt < fail:
        try:
            if is_proxy:
                response = requests.get(url, headers=headers, proxies=proxies, verify=True)
            else:
                response = requests.get(url, headers=headers)
            break
        except Exception as e:
            print(f'error info {e}')
        finally:
            cnt += 1

    return response


def producer(idx, item_url):
    try:
        item_html = get_request(item_url).text
        item = {'idx': idx, 'item_html': item_html, 'item_url': item_url}
        task_queue.put(item)  # 将获取的HTML放入任务队列
        with lock:  # 使用锁来更新进度条
            pbar.update(1)
    except requests.RequestException as e:
        print(f"请求错误: {e}, id号: {idx}, url: {item_url}")


def consumer():
    while True:
        item = task_queue.get()
        if item is None:  # 收到停止信号
            break
        try:
            data = {'idx': item['idx'], 'url': item['item_url']}
            data.update(extract_page_data(item['item_html']))
            result_queue.put(data)  # 将处理后的数据放入结果队列
        except Exception as e:
            print(f"处理错误: {e}, idx:{item['idx']}, url:{item['item_url']}")
        finally:
            task_queue.task_done()


def extract_page_data(response_text):
    data = {}
    item_html = BeautifulSoup(response_text, 'html.parser')
    json_text = [html.unescape(script) for script in item_html.find_all('script') if
                 script.get('type') == 'application/ld+json'][-1]
    json_data = json.loads(json_text.get_text())
    data['event'] = json_data['name'] if 'name' in json_data else None
    data['startDate'] = json_data['startDate'] if 'startDate' in json_data else None
    data['endDate'] = json_data['endDate'] if 'endDate' in json_data else None
    data['brand'] = json_data['image'] if 'image' in json_data else None
    data['description'] = json_data['description'] if 'description' in json_data else None
    data['organizer'] = json_data['organizer']['name'] if 'organizer' in json_data else None

    data['location'] = json_data['location']['name'] \
        if 'location' in json_data and 'name' in json_data['location'] else None
    data['addressLocality'] = json_data['location']['address']['addressLocality'] \
        if 'location' in json_data and 'address' in json_data['location'] \
           and 'addressLocality' in json_data['location']['address'] else None
    data['addressRegion'] = json_data['location']['address']['addressRegion'] \
        if 'location' in json_data and 'address' in json_data['location'] \
           and 'addressRegion' in json_data['location']['address'] else None
    data['addressCountry'] = json_data['location']['address']['addressCountry'] \
        if 'location' in json_data and 'address' in json_data['location'] \
           and 'addressCountry' in json_data['location']['address'] else None

    # 特化
    div_boxes_primary = [div for div in item_html.find_all('div')
                         if div.get('class') is not None and 'box-primary' in div.get('class')]
    data['category'] = div_boxes_primary[0].select('p > b')[0].get_text()

    data['attendance'] = None
    data['registration'] = None
    div_boxes_success = [div for div in item_html.find_all('div')
                         if div.get('class') is not None and 'box-success' in div.get('class')]
    for box in div_boxes_success:
        title = box.find('h3').get_text(strip=True)
        if title == 'Attendance Information':
            attendance_people = box.find_all(lambda tag: tag.name == 'p' and 'total people' in tag.get_text())
            data['attendance'] = attendance_people[0].get_text(strip=True) if attendance_people != [] else None

        elif title == 'Registration Information':
            box_body = box.find(attrs={'class': 'box-body'})
            data['registration'] = box_body.get_text()

    data['Guests'] = None
    div_boxes_info = [div for div in item_html.find_all('div')
                      if div.get('class') is not None and 'box-info' in div.get('class')]
    for box in div_boxes_info:
        title = box.find('h3').get_text(strip=True)
        if title.endswith('Guests'):
            data['Guests'] = '\n'.join([li.get_text() for li in box.find_all('li')])

    return data


def multi_thread(item_list, start, consumer_func, producer_func):
    # 启动消费者线程
    num_consumers = 1  # 消费者线程数量
    num_producers = 5  # 生产者线程数量
    consumers = []
    for _ in range(num_consumers):
        thread = Thread(target=consumer_func)
        thread.start()
        consumers.append(thread)

    # 使用ThreadPoolExecutor启动生产者线程
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_producers) as executor:
        for idx, item_url in enumerate(item_list):
            executor.submit(producer_func, start + idx, item_url)

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

    return item_info_dict_list


def single_thread(item_list, start):
    item_info_list = []
    for i in range(0, len(item_list)):
        url = url_list[i]

        response = get_request(url)
        if response is None:
            continue

        item_info = {'idx': start + i, 'url': url}
        item_info.update(extract_page_data(response.text))
        item_info_list.append(item_info)

        pbar.update(1)

    return item_info_list


def sleep_with_progress_tqdm(duration, interval=1):
    for _ in tqdm(range(int(duration)), desc="Sleeping"):
        time.sleep(interval)


for i in range(stpt, len(url_list), step):
    if i == bkpt:
        break

    pbar = tqdm(total=step)

    # data = single_thread(url_list[i:i + step], i)
    # task_queen共用一个最后总是会在第2轮卡住，具体原因不详!!!
    # 共享队列
    task_queue = queue.Queue()
    # 结果队列
    result_queue = queue.Queue()
    data = multi_thread(url_list[i:i + step], i, consumer, producer)
    pbar.close()
    json_saver(data, save_path, 'fancons_info_' + str(i + step))
    # sleep_with_progress_tqdm(30, 1)
