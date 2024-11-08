import requests
import re
import parsel
import os
import csv
import pandas as pd
import json

save_path_base = r'C:\Users\11435\Desktop\clutter\research\data\frd'
url_config_file_path = r'C:\Users\11435\Desktop\clutter\research\data\frd\url_config\url.txt'


# 额外功能的函数，用来判断给定文件中的url是否重复了
def is_duplicate(file_path):
    # 用于存储已经出现过的 URL 和它们首次出现的行号
    seen_urls = {}
    # 用于存储重复 URL 的行号
    duplicates = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_number, url in enumerate(f, start=1):
            # 去除 URL 末尾的换行符
            clean_url = url.strip()
            # 检查 URL 是否已经出现过
            if clean_url in seen_urls:
                # 如果出现过，记录重复的行号
                duplicates.setdefault(clean_url, []).append(line_number)
            else:
                # 如果没有出现过，记录首次出现的行号
                seen_urls[clean_url] = line_number

    # 输出重复的 URL 及其行号
    for url, lines in duplicates.items():
        print(f"URL '{url}' 重复出现在以下行: {lines}")


# 获取post和comment的原数据
def get_post_review(uid, post_index, root='https://weibo.com'):
    # 先对post进行抓取
    # cookie每次用都需要变一下
    cookies = {
        'UOR': 'cn.bing.com,app.weibo.com,cn.bing.com',
        'SINAGLOBAL': '5548902752922.988.1719907415638',
        'ULV': '1719907415639:1:1:1:5548902752922.988.1719907415638:',
        'SCF': 'Anb0ahMFX7Dviey6eY96snrouORkvhB_p5zpGSx2o7SuXCTKcZguAv0v1Lg_VZNrmXSk9WwhXtnH1wwTVdu6plY.',
        'ALF': '1727249333',
        'SUB': '_2A25LyF7lDeRhGeFG6VsX-CbNzzqIHXVopN4trDV8PUJbkNB-LU3MkW1Necmea46bIemBv3M_SxkWSP5yN3XNSQ_m',
        'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WhqByqKzdmhKOAefQHj9BFY5JpX5KMhUgL.FoMReo.c1hnpShq2dJLoIpiBqPiy9sL09CfBqPiydgHX9Pzt',
        'XSRF-TOKEN': 'TxWiv_QeRbCeEPmS3AQCogC3',
        'PC_TOKEN': '60b19c98dd',
        'WBPSESS': 'cr4hkwwxfJb_HtFDhT8YoAmRwnjKqHZB06W25MPP-Ghd2KXRxNilELUAmscFjd6-q0MIRNJSS43cBER1s-JOWZ1zcX33qHPlhTrPu8rXHGWaqYWRQUpuQvVYydH2lUWufHfqTW2f8NH7OnFKvqQFKA==',
    }

    headers = {
        'referer': '/'.join([root, uid, post_index]),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    }

    params = {
        'id': post_index,
        'locale': 'zh-CN',
    }

    post_url = 'https://weibo.com/ajax/statuses/show'
    response = requests.get(post_url, params=params, cookies=cookies, headers=headers)

    # post抓取到了以后，获得用于抓取post里comment的mid
    post_data = response.json()
    mid = post_data["mid"]

    comments_params = {
        'is_reload': '1',
        'id': mid,
        'is_show_bulletin': '2',
        'is_mix': '0',
        'count': '30',
        'uid': uid,
        'fetch_level': '0',
        'locale': 'zh-CN',
    }

    comments_url = 'https://weibo.com/ajax/statuses/buildComments'
    comments_response = requests.get(comments_url, params=comments_params, cookies=cookies, headers=headers)
    comments_data = comments_response.json()['data']
    return post_data, comments_data


# 对获取到的数据进行需要的提取与处理
def data_process(post_data, comments_data):
    # 对post信息进行处理，post关键字：
    # user_name, user_profile, uid, mid(id), post_text, post_img_url, repost_cnt转发, comments_cnt评论, likes_cnt点赞
    post_info = {'user_name': post_data['user']['screen_name'],
                 'user_profile': post_data['user']['profile_image_url'],
                 'uid': post_data['user']['id'],
                 'mid': post_data['mid'],
                 'post_text': post_data['text_raw'],
                 'repost_cnt': post_data['reposts_count'],
                 'comments_cnt': post_data['comments_count'],
                 'likes_cnt': post_data['attitudes_count']}
    # 处理图片信息，图片用url的方式进行json存储
    post_img_origin_url = []
    pic_infos = post_data['pic_infos']
    for pic_info in pic_infos:
        post_img_origin_url.append(pic_infos[pic_info]['original']['url'])
    post_info['post_img_url'] = post_img_origin_url

    # 对评论信息处理，comments关键字：
    # user_name, user_profile, gender, fans_cnt, subscribe_cnt, posts_cnt, big_fan铁粉等级, is_vip, comments, likes_cnt
    comments_info = {}
    for i in range(len(comments_data)):
        comment_info = {'user_name': comments_data[i]['user']['screen_name'],
                        'user_profile': comments_data[i]['user']['profile_image_url'],
                        'gender': comments_data[i]['user']['gender'],
                        'posts_cnt': comments_data[i]['user']['statuses_count'],
                        'fans_cnt': comments_data[i]['user']['followers_count'],
                        'subscribe_cnt': comments_data[i]['user']['friends_count'],
                        'is_vip': comments_data[i]['user']['fansIcon']['member_rank'],
                        'comments': comments_data[i]['text_raw'], 'likes_cnt': comments_data[i]['like_counts'],
                        'big_fan': comments_data[i]['user']['fansIcon']['icon_url']}

        # 对粉丝等级进行一个判定，比如铁粉钻粉
        # https://h5.sinaimg.cn/upload/114/962/2022/07/08/member_6_bigfan3_1.png vip等级6，3钻粉，1级
        comments_info[i] = comment_info

    data = {
        "post_data": post_info,
        "comments_data": comments_info
    }

    return data


# 对json数据进行保存
def save(data, post_index):
    # 目标文件路径
    file_path = '\\'.join([save_path_base, 'web-' + data['post_data']['user_name'], post_index + '.json'])

    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 现在可以安全地写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def url_split(url):
    # 移除 URL 的 # 后面的部分（如果存在）
    # url = 'https://weibo.com/1943171370/Ose8r3fPv#comment'
    url_without_hash = url.split('#')[0]

    # 拆分 URL 并提取 uid 和 post_index
    parts = url_without_hash.split('/')
    uid = parts[-2]  # 倒数第二个部分是 uid
    post_index = parts[-1]  # 最后一个部分是 post_index
    return uid, post_index


#  正式的代码编写
#  对url配置文件中的url进行读取，后爬取其中的评论
with open(url_config_file_path, 'r', encoding='utf-8') as f:
    for line_number, url in enumerate(f, start=1):
        uid, post_index = url_split(url)
        post_data, comments_data = get_post_review(uid=uid, post_index=post_index)
        data = data_process(post_data=post_data, comments_data=comments_data)
        save(data=data, post_index=post_index)
        if line_number == 3:
            break
