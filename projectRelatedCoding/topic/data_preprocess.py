from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import csv

# 假设 processed_texts 是已经处理好的中文语料库
processed_texts = [...]  # 语料列表

# 保存语料库到CSV文件
with open('processed_texts.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    for text in processed_texts:
        writer.writerow([text])  # 假设每行保存一个文本

# 之后，你可以加载这些语料
with open('processed_texts.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    loaded_texts = [row[0] for row in reader]

# -----------------------------------------
# 假设documents是一个文档列表，labels是对应的类别标签
documents = ["文档内容1", "文档内容2", ...]
labels = [0, 1, ...]

# 为每个类别收集文档
category_docs = {}
for doc, label in zip(documents, labels):
    if label not in category_docs:
        category_docs[label] = []
    category_docs[label].append(doc)

# 构建词频矩阵
vectorizer = CountVectorizer()
all_words = []
for category, docs in category_docs.items():
    docs_combined = " ".join(docs)
    all_words.extend(vectorizer.fit_transform([docs_combined]).toarray()[0])

# 计算所有词的词频
word_counts = Counter(all_words)

# 选择每个类别的高频词
top_words_per_category = {}
for category, docs in category_docs.items():
    category_words = " ".join(docs)
    category_counts = vectorizer.transform([category_words]).toarray()[0]
    top_words = [word for word, count in zip(word_counts, category_counts[0]) if count > 0]
    top_words_per_category[category] = top_words

# 打印每个类别的主题词
for category, top_words in top_words_per_category.items():
    print(f"Category {category} Top Words: {top_words}")
