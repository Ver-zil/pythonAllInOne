import os
import csv
import time
import gc
import math
from tqdm import tqdm
from openpyxl import load_workbook
import pandas as pd
from transformers import BertModel, BertTokenizer
import torch
import torch.nn as nn

from utils.reader import json_reader
from utils.saver import json_saver
import concurrent.futures

dir_path = r'C:\Users\11435\Desktop\clutter\research\data\topicModels\JD\processed\raw1'
out_dir = r'C:\Users\11435\Desktop\clutter\research\data\topicModels\JD\processed\raw1'

# 加载预训练的BERT模型和分词器
model_path = r'D:\tool\toolkit\nlp\bert-base-chinese'
model = BertModel.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained(model_path)

# 将模型移动到GPU（如果可用）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


# 定义函数计算文本嵌入
def get_sentence_embedding(sentence, tokenizer, model):
    inputs = tokenizer(sentence, return_tensors='pt', padding=True, truncation=True, max_length=128)

    # 将输入数据移动到与模型相同的设备（CPU或GPU）
    inputs = {key: val.to(device) for key, val in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
    # 使用CLS token的隐藏状态作为句子的嵌入
    sentence_embedding = outputs.last_hidden_state[:, 0, :]
    return sentence_embedding.squeeze()  # 移除批次维度


def get_file_data(dir_path, fid):
    data = json_reader(dir_path, fid)
    return data


def single_convert(data):
    """
    :param data: data就是原始的review_infos array list
    :return:
    """
    for idx, review_info in enumerate(data):
        data[idx]['bert_features'] = get_sentence_embedding(review_info['review'], tokenizer, model)


def batch_convert(texts, batch_size=1000):
    bert_features = []
    for i in range(0, len(texts), batch_size):
        end = min(len(texts), i + batch_size)
        res = get_sentence_embedding(texts[i: end], tokenizer, model).tolist()
        bert_features = bert_features + res
    return bert_features


data = get_file_data(dir_path, "data_integration")
texts = [review_info['review'] for review_info in data]
bert_features = batch_convert(texts)
for idx in range(len(data)):
    data[idx]['bert_features'] = bert_features[idx]
json_saver(data, out_dir, "data_integration1")
