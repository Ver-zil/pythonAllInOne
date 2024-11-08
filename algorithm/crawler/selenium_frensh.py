from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

url = 'https://tb.alicdn.com/'

options = Options()
options.add_argument(r"--user-data-dir=C:\Users\11435\AppData\Local\Google\Chrome\User Data")  # 指定用户数据目录
# options.add_argument(r"--user-data-dir=C:\Users\11435\Desktop\clutter\cache\python\chrome")  # 该数据目录专门给收集cookies时使用

# 指定 ChromeDriver 的路径
service = Service(executable_path=r'D:\tool\toolkit\driver\chromedriver.exe')

# 使用 Service 创建 WebDriver 实例
driver = webdriver.Chrome(service=service, options=options)
driver.get(url)
