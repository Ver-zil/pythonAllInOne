import os
import json


def txt_line_reader(file):
    lines_list = []
    # 打开txt文件，读取每一行
    with open(file, 'r', encoding='utf-8') as file:
        for line in file:
            # 将每一行的内容去除末尾的换行符并添加到列表中
            lines_list.append(line.strip())

    return lines_list


def json_reader(dir_path, fid):
    """
    :param data: json数据
    :param dir_path: 保存文件夹地址
    :param fid: 文件标识
    :return:
    """
    # 目标文件路径
    file_path = '\\'.join([dir_path, fid + '.json'])

    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 现在可以安全地写入文件
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    return data
