from sympy import hessian
import sympy as sym
import numpy as np

# 如果不导入hessian 就使用sympy.matrices.dense.hessian
x1, x2 = sym.symbols('x1 x2')
f3 = x1 ** 2 + sym.log(x2)
print(hessian(f3, (x1, x2)))

a1 = 5e4
a2 = -5e3
a3 = 40
a4 = -1
a5 = -2e-2
e1 = 1e5
e2 = 2
epsilon = 0.1
dis = lambda p1, p2: ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

y, z = sym.symbols('y z')
x = a1 + a2 * y + a3 * z + a4 * y * z + a5 * z ** 2
g2 = e1 + e2 * x
E = y * x - (z + g2)
target = sym.Matrix([-E])
init = sym.Matrix([[np.random.randint(10)], [np.random.randint(10)]])


def steepest_descent():
    print(f'the steepest descent method init point is {init}')
    cur = init
    while True:
        grad = target.jacobian([y, z]).subs([(y, cur[0]), (z, cur[1])]).T
        h = hessian(target, (y, z)).subs([(y, cur[0]), (z, cur[1])])
        t = grad.T * grad * (grad.T * h * grad) ** (-1)
        next_point = cur - t[0, 0] * grad
        print(f'the next point is {next_point[0], next_point[1]} ,'
              f' f value is {target.subs([(y, next_point[0]), (z, next_point[1])])}')
        if dis(cur, next) < epsilon:
            break
        cur = next


def newton():
    print(f'the newton method init point is {init}')
    cur = init
    while True:
        h = hessian(target, (y, z)).subs([(y, cur[0]), (z, cur[1])])
        grad = target.jacobian([y, z]).subs([(y, cur[0]), (z, cur[1])]).T
        next_point = cur - h ** (-1) * grad
        print(f'the next point is {next_point[0], next_point[1]} ,'
              f' f value is {target.subs([(y, next_point[0]), (z, next_point[1])])}')
        if dis(cur, next_point) < epsilon:
            break
        cur = next_point


steepest_descent()
newton()
