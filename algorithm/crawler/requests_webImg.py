import requests
import time
import os

# 用来抓web相册图片的

base_url = 'https://weibo.com/ajax/profile/getImageWall'
base_img_url = 'https://wx1.sinaimg.cn/large'
base_save_path = r'C:\Users\11435\Desktop\clutter\img\beaut\sanako'
uid = '5246524190'

cookies = {
    'UOR': 'cn.bing.com,app.weibo.com,cn.bing.com',
    'SINAGLOBAL': '5548902752922.988.1719907415638',
    'ULV': '1719907415639:1:1:1:5548902752922.988.1719907415638:',
    'SCF': 'Anb0ahMFX7Dviey6eY96snrouORkvhB_p5zpGSx2o7SuXCTKcZguAv0v1Lg_VZNrmXSk9WwhXtnH1wwTVdu6plY.',
    'XSRF-TOKEN': 'ZFhV9KLIfsqttrAoL_WgS2Nn',
    'PC_TOKEN': '19e9de172a',
    'SUB': '_2A25L8JPuDeRhGeFG6VsX-CbNzzqIHXVoj6kmrDV8PUNbmtAGLUPBkW9NecmeazaoFrut2pxQgRsjMxCxFJVyoKtS',
    'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WhqByqKzdmhKOAefQHj9BFY5JpX5KzhUgL.FoMReo.c1hnpShq2dJLoIpiBqPiy9sL09CfBqPiydgHX9Pzt',
    'ALF': '02_1729917117',
    'WBPSESS': 'cr4hkwwxfJb_HtFDhT8YoAmRwnjKqHZB06W25MPP-Ghd2KXRxNilELUAmscFjd6-8-kM9ls18e0vtY_PbL40Kl4CsosThM4VTAgEDhT5WAU6CDYR-kwfGI7IAA3AROoJI0sOZKURn24uzFjtk3xoBQ==',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'client-version': 'v2.46.6',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://weibo.com/u/5246524190?tabtype=album',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'server-version': 'v2024.08.28.1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'x-xsrf-token': 'TxWiv_QeRbCeEPmS3AQCogC3',
}

params = {
    'uid': uid,
    'sinceid': '0',
    'has_album': 'true',
}


def save_img(save_path, img_url):
    # 如果图片存在，就不用再次下载
    if not os.path.exists(save_path):
        img_response = requests.get(img_url, headers=headers)
        if img_response.status_code == 200:
            # 打开文件准备写入
            with open(save_path, 'wb') as f:
                # 将图片数据写入文件
                f.write(img_response.content)
            print('图片保存成功')
        else:
            print('图片下载失败，状态码：', img_response.status_code)
    else:
        print('图片已存在，跳过下载。')


last_month = "-1"
order = 0
bkpt = '202002'
for i in range(30):
    response = requests.get(base_url, params=params, cookies=cookies, headers=headers)
    img_list = response.json()['data']['list']
    since_id = response.json()['data']['since_id']
    for i in range(len(img_list)):
        pid = img_list[i]['pid']
        img_url = '/'.join([base_img_url, pid + '.jpg'])

        current_month = img_list[i]['timeline_month'] if img_list[i]['timeline_month'] != '' else last_month

        # timeline_year不为空，则采用timeline_year
        year = '2024' if params['sinceid'] == '0' else params['sinceid'].split('_')[-2][:4]
        if img_list[i]['timeline_year'] != '':
            year = img_list[i]['timeline_year']

        # 如果当前月份与上次图片的月份不一定，图片顺序order重新变成1
        if current_month != last_month:
            order = 1
        else:
            order += 1

        if year + current_month == bkpt:
            break
        img_name = year + current_month + (str(order) if order >= 10 else ('0' + str(order)))
        path = '\\'.join([base_save_path, img_name + '.jpg'])
        save_img(save_path=path, img_url=img_url)
        print(img_name)

        last_month = current_month

    params['sinceid'] = since_id
    time.sleep(0.2)
