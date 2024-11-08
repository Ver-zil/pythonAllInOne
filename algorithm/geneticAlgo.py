import numpy as np
import matplotlib.pyplot as plt

# 使用np.eye(2)生成单位矩阵,然后乘以一个随机生成得均匀分布值组成单位矩阵得值
x0 = np.random.multivariate_normal(np.random.uniform(-50, 0, 2), np.eye(2) * np.random.uniform(8, 30, 2), 1000)
x1 = np.random.multivariate_normal(np.random.uniform(0, 50, 2), np.eye(2) * np.random.uniform(2, 10, 2), 1000)
# x=np.append(x0,x1,axis=0)
# x2 = np.random.multivariate_normal(np.random.uniform(-50,50,2), np.eye(2)*np.random.uniform(5,20,2), 1000)
# #numpy中append得用法
# x=np.append(x,x2,axis=0)
x2 = np.array([0] * 100)
x2y = np.arange(-50, 50, 100)
# 将生成得图可视化

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.scatter(x0[:, 0], x0[:, 1])
plt.scatter(x1[:, 0], x1[:, 1])
plt.xlabel('x1')
plt.ylabel('x2')
# plt.show()
# plt.savefig(r'C:\Users\11435\Desktop\clutter\plot.png')
