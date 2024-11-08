from DrissionPage import ChromiumPage, ChromiumOptions
from utils.saver import json_saver
import pickle
import time

base_save_path = r'C:\Users\11435\Desktop\clutter\research\data\roommate\game'
with open('\\'.join([base_save_path, 'item_id.pkl']), 'rb') as f:
    item_id_lists = pickle.load(f)

for i in range(15):
    url = f'https://steamdb.info/app/{item_id_lists[i]}/'

    dp = ChromiumPage()
    dp.get(url)

    time.sleep(1)

    # dp.ele("xpath://*[@id='gLIfn4']/div/label/input").click()
    #
    # cookies = dp.cookies()
    # json_saver(cookies, base_save_path, "cookies")