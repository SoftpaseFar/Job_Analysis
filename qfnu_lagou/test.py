import requests

if __name__ == '__main__':
  import requests

  # 要访问的目标页面
  targetUrl = "http://test.abuyun.com"
  # targetUrl = "http://proxy.abuyun.com/switch-ip"
  # targetUrl = "http://proxy.abuyun.com/current-ip"

  # 代理服务器
  proxyHost = "http-dyn.abuyun.com"
  proxyPort = "9020"

  # 代理隧道验证信息
  proxyUser = "HHB497K062L87CBD"
  proxyPass = "141A79CA80999658"

  proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
  }

  proxies = {
    "http": proxyMeta,
    "https": proxyMeta,
  }

  resp = requests.get(targetUrl, proxies=proxies)

  print(resp.status_code)

  print(resp.text)
