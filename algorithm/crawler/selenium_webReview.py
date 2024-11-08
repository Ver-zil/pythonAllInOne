import re
import parsel
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from selenium.common.exceptions import TimeoutException
import prettytable
import time


def save_img(url, save_img_path):
    # url = 'https://wx2.sinaimg.cn/orj360/73d2712agy1hsu5vds946j22c0340x6r.jpg'

    headers = {
        'referer': 'https://weibo.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # 打开文件准备写入
        with open(save_img_path, 'wb') as file:
            # 将图片数据写入文件
            file.write(response.content)
        print('图片保存成功')
    else:
        print('图片下载失败，状态码：', response.status_code)


# 指定 ChromeDriver 的路径
service = Service(executable_path=r'D:\tool\toolkit\chromedriver.exe')

# 使用 Service 创建 WebDriver 实例
driver = webdriver.Chrome(service=service)

user = '1943171370'

url = 'https://weibo.com/u/' + user
save_path = r'C:\Users\11435\Desktop\clutter\research\data\\'
driver.get(url)

# 等待页面加载完成，可能需要一些时间
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Feed_body_3R0rO')))

# for i in range(2):
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

html = driver.find_element(By.CSS_SELECTOR, 'html')
html.send_keys(Keys.END)

time.sleep(3)


i = 0
# 找到整个帖子的的div
posts = driver.find_elements(By.CSS_SELECTOR, 'article.woo-panel-main')[i]
driver.execute_script("arguments[0].scrollIntoView();", posts)
time.sleep(1)
posts_body = driver.find_elements(By.CSS_SELECTOR, 'div.Feed_body_3R0rO')[i]
posts_footer = driver.find_elements(By.CSS_SELECTOR, 'footer')[i]
print("2")
#  找到整个帖子里的消息图标按钮
comment_button = driver.find_elements(By.CSS_SELECTOR, '.toolbar_commentIcon_3o7HB')[i]
print("3")

# 创建 ActionChains 对象
action_chains = ActionChains(driver)
# 模拟鼠标悬停和点击
action_chains.move_to_element(comment_button).perform()
action_chains.click(comment_button).perform()

# # 定位"打开全部评论位置"
# # 点开评论后点击查看全部评论
# more_comment = posts.find_element(By.CSS_SELECTOR, 'RepostCommentFeed_more_idG8i')
# action_chains.move_to_element(more_comment).perform()
# action_chains.click(more_comment).perform()
