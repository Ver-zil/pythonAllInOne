import xgboost as xgb
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 加载波士顿房价数据集
boston = load_boston()
X = boston.data
y = boston.target

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 将数据转换为 DMatrix 格式
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# 定义模型参数
params = {
    'objective': 'reg:squarederror',  # 回归任务
    'eval_metric': 'rmse'  # 评估指标
}

# 训练模型
epochs = 100
evals_result = {}
model = xgb.train(params, dtrain, epochs, evals=[(dtrain, 'train'), (dtest, 'test')], evals_result=evals_result)
print("Training Loss:", evals_result['train']['rmse'][-1])

# 预测
preds = model.predict(dtest)

# 计算均方根误差（RMSE）
rmse = mean_squared_error(y_test, preds, squared=False)
print("RMSE:", rmse)
