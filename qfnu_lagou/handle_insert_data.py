from collections import Counter

from qfnu_lagou.create_lagou_tables import Lagoutables
from qfnu_lagou.create_lagou_tables import Session
import time


class HandleLagou(object):
  def __init__(self):
    # 实例化Session信息
    self.mysql_session = Session()
    # 今天
    self.date = time.strftime("%Y-%m-%d", time.localtime())

  # 数据的存储方法
  def insert_item(self, item):

    # 存储的数据结构
    data = Lagoutables(
      # 岗位ID
      positionID=item['positionId'],
      # 经度
      longitude=item['longitude'],
      # 纬度
      latitude=item['latitude'],
      # 岗位名称
      positionName=item['positionName'],
      # 工作年限
      workYear=item['workYear'],
      # 学历
      education=item['education'],
      # 岗位性质
      jobNature=item['jobNature'],
      # 公司类型
      financeStage=item['financeStage'],
      # 公司规模
      companySize=item['companySize'],
      # 业务方向
      industryField=item['industryField'],
      # 所在城市
      city=item['city'],
      # 岗位标签
      positionAdvantage=item['positionAdvantage'],
      # 公司简称
      companyShortName=item['companyShortName'],
      # 公司全称
      companyFullName=item['companyFullName'],
      # 公司所在区
      district=item['district'],
      # 公司福利标签
      companyLabelList=','.join(item['companyLabelList']),
      salary=item['salary'],
      # 抓取日期
      crawl_date=self.date
    )

    print(item)
    # 在存储数据之前，先来查看一下表里是否有这条岗位信息
    query_result = self.mysql_session.query(Lagoutables).filter(Lagoutables.crawl_date == date,
                                                                Lagoutables.positionID == item['positionId']).first()

    if query_result:
      print('该岗位信息已经存在%s:%s:%s' % (item['positionId'], item['city'], item['positionName']))
    else:
      # 插入数据
      self.mysql_session.add(data)
      # 提交数据到数据库
      self.mysql_session.commit()
      print('新增岗位信息%s:%s:%s' % (item['positionId'], item['city'], item['positionName']))

  def query_industryfield_result(self):
    info = {}
    # 查询今日抓取的数据
    result = self.mysql_session.query(Lagoutables.industryField).filter(
      # Lagoutables.crawl_date == self.date
    ).all()
    result_list1 = [str(x[0]).split(',')[0] for x in result]
    result_list2 = [x for x in Counter(result_list1).items()]
    # 填充的是series里的数据
    data = [{"name": x[0], "value": x[1]} for x in result_list2]
    name_list = [x['name'] for x in data]
    print(name_list)
    info['x_name'] = name_list
    info['data'] = data
    return info


lagou_mysql = HandleLagou()
lagou_mysql.query_industryfield_result()
