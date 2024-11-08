# selenium

- **chrome版本126.0.6478.x**
- selenium操作有个问题
  - 因为是真的去模拟浏览器本身的操作，操作与操作之间需要加sleep(1)，否则会出问题
  - 在执行点击按钮的时候，也需要将其拉到屏幕的对应位置

# requests

- cookies每次使用的时候可能需要重新设置
- get请求的时候把proxy关了

