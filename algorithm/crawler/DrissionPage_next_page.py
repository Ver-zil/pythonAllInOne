# 本项目主要用来测试页面数量
from DrissionPage import ChromiumPage, ChromiumOptions
import time

url = 'https://item.jd.com/100057734134.html#comment'
page_num = 90
dp = ChromiumPage()
dp.get(url)

model = "chaping"

product_valuation = {
    "normal": 0,
    "haoping": 1,
    "zhongping": 1,  # 90
    "chaping": 2  # 90
}

if model != "normal":
    dp.ele("css:[clstag='shangpin|keycount|product|" + model + "']").click()

for i in range(page_num):
    time.sleep(0.5)
    dp.eles("css:.ui-pager-next")[product_valuation[model]].click()
    print(i)
