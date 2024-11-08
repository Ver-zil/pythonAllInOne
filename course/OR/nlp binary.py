import numpy as np

f = lambda x: 10 * x + 70 / x

a = 1
b = 10
delta = 0.99e-1
epo = 0
while True:
    epo += 1
    t1 = (a + b - delta) / 2
    t2 = (a + b + delta) / 2
    if b - a <= 1e-1:
        break
    print(f'current epo:{epo}  area:[{round(a, 2)},{round(b, 2)}]  delta:{b - a}')
    if f(t1) <= f(t2):
        b = t2
    else:
        a = t1
