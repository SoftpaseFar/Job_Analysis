import json
import re
import time
import requests
import multiprocessing
from qfnu_lagou.handle_insert_data import lagou_mysql


class HandleLaGou(object):
  def __init__(self):
    # 使用session保存cookies信息
    self.lagou_session = requests.session()
    self.header = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    self.city_list = ""

  # 获取全国所有城市列表的方法
  def handle_city(self):
    # print('start')
    city_search = re.compile(r'<li >\s+<a href=.*?>(.*?)</a>')
    city_url = "https://www.lagou.com/jobs/allCity.html"
    # print('1')
    city_result = self.handle_request(method="GET", url=city_url)
    # 使用正则表达式获取城市列表
    # print('2')
    self.city_list = city_search.findall(city_result)
    self.lagou_session.cookies.clear()
    # print('end')

  def handle_city_job(self, city):
    first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" % city
    first_response = self.handle_request(method="GET", url=first_request_url)
    total_page_search = re.compile(r'<span class="span totalNum">(\d+)</span>')

    try:
      total_page = total_page_search.search(first_response).group(1)
      # print(total_page)
    # 由于没有岗位信息造成exception
    except:
      return
    else:
      for i in range(1, int(total_page) + 1):
        data = {
          "pn": i,
          "kd": "python"
        }
        page_url = "https://www.lagou.com/jobs/positionAjax.json?city=%s&needAddtionalResult=false" % city
        referer_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" % city
        # referer的URL需要进行encode
        self.header['Referer'] = referer_url.encode()
        response = self.handle_request(method="POST", url=page_url, data=data, info=city)
        lagou_data = json.loads(response)
        job_list = lagou_data['content']['positionResult']['result']
        for job in job_list:
          # print(job)
          lagou_mysql.insert_item(job)

  def handle_request(self, method, url, data=None, info=None):
    while True:
      # 加入阿布云的动态代理
      # 代理服务器
      proxyHost = "http-dyn.abuyun.com"
      proxyPort = "9020"

      proxyUser = "HOQ116481LBTJU8D"
      proxyPass = "DD2B287D885E0C03"

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

      try:
        if method == "GET":
          response = self.lagou_session.get(url=url, headers=self.header, proxies=proxies, timeout=6)
        elif method == "POST":
          response = self.lagou_session.post(url=url, headers=self.header, data=data, proxies=proxies, timeout=6)
        response.encoding = 'utf-8'
      except:
        # 需要先清除cookie信息
        self.lagou_session.cookies.clear()
        # 重新获取cookie信息
        first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" % info
        self.handle_request(method="GET", url=first_request_url)
        time.sleep(10)
        continue
      if '频繁' in response.text:
        print('频繁', response.text)
        # 需要先清除cookie信息
        self.lagou_session.cookies.clear()
        # 重新获取cookie信息
        first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" % info
        self.handle_request(method="GET", url=first_request_url)
        time.sleep(10)
        continue
      return response.text


if __name__ == '__main__':
  lagou = HandleLaGou()
  # 获取所有城市方法
  lagou.handle_city()

  # 引入多进程的方法加速抓取
  pool = multiprocessing.Pool(2)

  for city in lagou.city_list:
    pool.apply_async(lagou.handle_city_job, args=(city,))
  pool.close()
  pool.join()
