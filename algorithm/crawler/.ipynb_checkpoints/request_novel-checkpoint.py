import requests
import re
import parsel
import httpx

url = 'https://www.biqudu.com/0_390/74866133.html'
url403 = 'https://www.beqege.cc/2/21.html'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# client = httpx.Client(http2=True)
# response = client.get(url, timeout=30)
response = requests.get(url, headers=headers)
print(response.text)

title = re.findall('<h1>(.*?)</h1>', response.text)
content = re.findall('<div id="content" class="showtxt">(.*?)</div>', response.text)
print(title, '\n', content)
