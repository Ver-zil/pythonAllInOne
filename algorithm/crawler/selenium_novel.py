from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# 指定 ChromeDriver 的路径
service = Service(executable_path=r'D:\tool\toolkit\chromedriver.exe')

# 使用 Service 创建 WebDriver 实例
driver = webdriver.Chrome(service=service)
