import os
import json
from utils.saver import json_saver

base_dir = r'C:\Users\11435\Desktop\clutter\research\data\topicModels\JD'
name = 'data_integration'


def recurrent_dir(dir_path, parent=0):
    # 0表示当前目录，1上一级目录
    data = None
    for file_or_dir__name in os.listdir(dir_path):
        file_or_dir__path = os.path.join(dir_path, file_or_dir__name)
        if parent and os.path.isdir(file_or_dir__path):
            new_data = recurrent_dir(file_or_dir__path, parent - 1)
        else:
            new_data = get_file_data(file_or_dir__path)
        data = new_data if data is None else integration(data, new_data)

    return data


def get_file_data(file_path):
    if file_path.endswith(".json"):
        with open(file_path, 'rb') as f:
            data = json.load(f)
    else:
        data = None
    return data


def integration(pre_data, new_data):
    if new_data is not None:
        for k, v in new_data.items():
            pre_data[k] = pre_data[k] + v
    return pre_data


def save_data(data, save_dir, fid):
    json_saver(data, save_dir, fid)


all_data = recurrent_dir(base_dir, 1)
save_data(all_data, base_dir, name)
