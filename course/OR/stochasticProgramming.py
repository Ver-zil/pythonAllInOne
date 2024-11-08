import numpy as np
import cvxpy as cp

# 随机规划作业
climax = np.array([1.2, 1, 0.8])
prob = np.array([1, 1, 1])
product = np.array([2.5, 3, 20])
sale_price = np.array([170, 150, 36, 10])
cost = np.array([150, 230, 260])
purchase_price = np.array([238, 210])
mini_demand = np.array([200, 240])

res = []

for i in range(len(prob)):
    product_ = product * climax[i]
    # x1,x2,x3,y1,w1,y2,w2,w3,w4
    z = np.array([150, 230, 260, 238, -170, 210, -150, -36, -10])
    con1 = [1, 1, 1, 0, 0, 0, 0, 0, 0]
    con2 = [-product_[0], 0, 0, -1, 1, 0, 0, 0, 0]
    con3 = [0, -product_[1], 0, 0, 0, -1, 1, 0, 0]
    con4 = [0, 0, -product_[2], 0, 0, 0, 0, 1, 1]
    con5 = [0, 0, 0, 0, 0, 0, 0, 1, 0]
    b1, b2, b3, b4, b5 = 500, -200, -240, 0, 6000
    A = np.array([con1, con2, con3, con4, con5])
    b = np.array([b1, b2, b3, b4, b5])
    x = cp.Variable(9, pos=True)
    obj = cp.Minimize(z @ x)
    con = [A @ x <= b]
    p = cp.Problem(obj, con)
    p.solve(solver='GLPK_MI')
    res.append(p.value)
    print()
    print(f'x value is {x.value}')  # x的最优解
    print(f'the min value is {p.value} \n')  # 最优值

res = np.array(res)
E = (res * prob / prob.sum()).sum()
print(f'res = {res} , E = {E}')
