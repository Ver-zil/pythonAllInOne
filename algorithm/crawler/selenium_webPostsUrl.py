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


# 该文件主要是通过动态抓取web某个V里所有贴子详细页面评论url的


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


#  判断帖子是否是目标贴，相当于进行一次筛选
def post_is_ok():
    pass


def get_driver(executable_path=r'D:\tool\toolkit\chromedriver.exe'):
    # 使用 Service 创建 WebDriver 实例
    service = Service(executable_path=executable_path)
    return webdriver.Chrome(service=service)


driver = get_driver()

user = '1943171370'

url = 'https://weibo.com/u/' + user
save_path = r'C:\Users\11435\Desktop\clutter\research\data\\'
driver.get(url)

# 等待页面加载完成，可能需要一些时间
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Feed_body_3R0rO')))

# 执行按钮下拉操作
html = driver.find_element(By.CSS_SELECTOR, 'html')
html.send_keys(Keys.END)

# 等待页面加载完毕再进行其他操作
time.sleep(3)
posts_url_list = []

for i in range(2):
    # 找到整个帖子的的div
    posts = driver.find_elements(By.CSS_SELECTOR, 'article.woo-panel-main')[i]
    driver.execute_script("arguments[0].scrollIntoView();", posts)
    time.sleep(2)
    posts_body = posts.find_element(By.CSS_SELECTOR, 'div.Feed_body_3R0rO')
    posts_footer = posts.find_element(By.CSS_SELECTOR, 'footer')
    print("2")
    #  找到整个帖子里的消息图标按钮
    comment_button = posts_footer.find_element(By.CSS_SELECTOR, '.toolbar_commentIcon_3o7HB')
    print("3")

    # 创建 ActionChains 对象
    action_chains = ActionChains(driver)
    # 模拟鼠标悬停和点击
    action_chains.move_to_element(comment_button).perform()
    action_chains.click(comment_button).perform()
    time.sleep(3)

    comments = posts.find_element(By.CSS_SELECTOR, 'div.Feed_box_3fswx div[transform-text]')
    whole_posts_href = comments.find_elements(By.TAG_NAME, 'a')[-1]
    print(whole_posts_href.get_attribute('href'))
    posts_url_list.append(whole_posts_href.get_attribute('href'))
    # for href in comments.find_elements(By.TAG_NAME, 'a'):
    #     print(href.get_attribute('href'))
    #     if href.get_attribute('href') is not None and href.get_attribute('href').endswith("#comment"):
    #         print(f"找到以 '#comment' 结尾的 href: {href}")
    #         # 执行你需要的操作，例如点击链接
    #         # a_tag.click()
    #         break  # 如果只关心第一个匹配项，找到后可以退出循环

