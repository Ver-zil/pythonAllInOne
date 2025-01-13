import os
import json
from utils.saver import json_saver
import re
import pandas as pd

base_dir = r'C:\Users\11435\Desktop\clutter\research\data\topicModels\JD\smart_phone'
name = 'data_integration'


def recurrent_dir(dir_path, parent=0):
    # 0表示当前目录，1上一级目录
    data = None
    for file_or_dir_name in os.listdir(dir_path):
        file_or_dir_path = os.path.join(dir_path, file_or_dir_name)
        if parent and os.path.isdir(file_or_dir_path):
            new_data = recurrent_dir(file_or_dir_path, parent - 1)
        else:
            new_data = get_file_data(file_or_dir_path)
        data = new_data if data is None else integration(data, new_data)

    return data


def get_file_data(file_path):
    data = None
    needed_prefix = False
    prefix = ''
    match = re.match(prefix + r'(\d+)', os.path.basename(file_path)) if needed_prefix else True
    if file_path.endswith(".json") and match:
        with open(file_path, 'rb') as f:
            data = json.load(f)

    # 对数据进行额外加工
    process_data = []
    for k, v in data.items():
        for idx, info in enumerate(v):
            v[idx]['review_type'] = k
        process_data = process_data + v
    return process_data


def integration(pre_data, new_data):
    if pre_data is None:
        return new_data
    if new_data is not None:
        pre_data = pre_data + new_data
    return pre_data


def save_data(data, save_dir, fid):
    json_saver(data, save_dir, fid)


all_data = recurrent_dir(base_dir, 0)
# save_data(all_data, base_dir, name)
