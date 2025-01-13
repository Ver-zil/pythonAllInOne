from DrissionPage import ChromiumPage, ChromiumOptions
import csv
import time
from utils.saver import json_saver


def get_review_infos(data):
    review_infos = [{
        'review': comment['content'],
        'review_time': comment['creationTime'],
        'score': comment['score'],
        'img_cnt': 0 if 'imageCount' not in comment else comment['imageCount']
    } for comment in data['comments']]

    return review_infos


base_save_path = r'C:\Users\11435\Desktop\clutter\research\data\topicModels\JD\smart_phone'

url = 'https://item.jd.com/100148810780.html#comment'
page_num = 10
product_id = url.split('/')[-1].split('.')[0]
dp = ChromiumPage()
# dp.driver.maximize_window()
dp.listen.start('api.m.jd.com/?appid=item-v3&functionId=pc_club_productPageComments')
dp.get(url)

review_info_list = {}

# 0号位是index
product_valuation = {
    "haoping": [1, 30],
    "zhongping": [2, 10],
    "chaping": [3, 30]
}

for k, v in product_valuation.items():

    # v[0]是page_ele_index，v[1]是对应评价的page_num
    dp.ele("css:[clstag='shangpin|keycount|product|" + k + "']").click()
    review_infos_ = []

    # if k not in ["chaping"]:
    #     continue

    for i in range(v[1]):
        if (i + 1) % 30 == 0:
            time.sleep(30)
        response = dp.listen.wait()
        json_data = response.response.body
        review_infos_ = review_infos_ + get_review_infos(json_data)

        time.sleep(5)
        try:
            dp.eles("css:.ui-pager-next")[v[0]].click()
        except Exception as e:
            user_input = input("是否解决问题[y/n]")
            if user_input == 'y':
                break

    review_info_list[k] = review_infos_

json_saver(review_info_list, base_save_path, product_id)
