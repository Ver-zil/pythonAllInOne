import json
import csv
import os


def save_img(save_path, img_content):
    """
    :param save_path: 保存路径
    :param img_content: 图片数据，对于response就是response.content
    :return:
    """
    # 打开文件准备写入
    with open(save_path, 'wb') as f:
        # 将图片数据写入文件
        f.write(img_content.content)
    print('图片保存成功')


def json_saver(data, dir_path, fid):
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
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def csv_saver(data, dir_path, fid):
    # 目标文件路径
    file_path = '\\'.join([dir_path, fid + '.csv'])
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        # 指定字典的键作为列标题
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # 写入列标题
        writer.writeheader()

        # 写入字典数据
        for row in data:
            writer.writerow(row)
