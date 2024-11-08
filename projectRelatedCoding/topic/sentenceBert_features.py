import torch
from joblib import dump, load
from transformers import BertModel, BertTokenizer

doc_data = []
dataset_name = ''
save_path = r'C:\Users\11435\Desktop\clutter\research\data\topicModels' + dataset_name + '.joblib'

# 加载已经训练好的bert模型
model_path = r'D:\tool\toolkit\nlp\distiluse-base-multilingual-cased-v2-finetuned-stsb_multi_mt-es'
model = BertModel.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained(model_path)

bert_features = []
for article in doc_data:
    # 对文章进行分词和编码
    encoded_input = tokenizer(article, return_tensors='pt', padding=True, truncation=True, max_length=512)
    # 获取模型的输出
    with torch.no_grad():
        outputs = model(**encoded_input)
    # 获取CLS token的嵌入作为文章的特征向量
    bert_features.append(outputs.last_hidden_state[:, 0, :].squeeze().detach().numpy())

# 保存特征向量到文件
# with open('features.pkl', 'wb') as f:
#     pickle.dump(features, f)
dump(bert_features, save_path)

# 之后，你可以加载这些特征向量
# loaded_features = load('features.joblib')
