#-*- coding:utf-8 -*-
# 划分训练集和测试集

import sys
import time
import pandas as pd

class DivisionTest:
    def __init__(self, path):
        self.path = path

    # 根据月份划分，前两月为训练集，后一月为测试集
    def monthDivision(self, date=20170900):
        self.ratings = pd.read_excel(self.path)
        # 划分训练集和测试集
        self.train, self.test = self.ratings[self.ratings[u'点播日期'] < date], self.ratings[self.ratings[u'点播日期'] > date]
        print u"训练集大小：" + str(len(self.train))
        print u"测试集大小：" + str(len(self.test))

    # 根据时间划分，天数之前为训练集，天数之后为测试集
    def hourDivision(self):
        df = pd.read_excel(u'F:\\postgraduate\\期刊论文\\用户单片点播信息.xlsx')
        # 选取训练集时间范围
        s1 = pd.Timestamp("2017-7-30 10:00:00")
        s2 = pd.Timestamp("2017-7-30 12:00:00")
        # 选取测试集时间范围
        e1 = s2
        e2 = pd.Timestamp("2017-7-30 14:00:00")
        # 划分训练集和测试集
        tr = df[df[ u"观看开始时间"] > s1]
        self.train = tr[tr[u"观看开始时间"] < s2]
        te = df[df[u"观看结束时间"] > e1]
        self.test = te[te[u"观看结束时间"] < e2]
        print u"训练集大小：" + str(len(self.train))
        print u"测试集大小：" + str(len(self.test))

    # 根据时间划分，天数之前为训练集，天数之后为测试集
    def allDivision(self):
        df = pd.read_excel(u'F:\\postgraduate\\期刊论文\\用户单片点播信息.xlsx')
        self.train = df


    # 保存训练集和测试集
    def saveCSV(self, method='month', date=20170900):
        if method == 'month':
            self.monthDivision(date)
            self.train.to_csv("train_data.csv", encoding="gbk", index=False)  # 写入到csv时，不要将索引写入index = False
            self.test.to_csv("test_data.csv", encoding="gbk", index=False)  # 写入到csv时，不要将索引写入index = False
        if method == 'hour':
            self.hourDivision()
            self.train.to_csv("train_data.csv", encoding="gbk", index=False)  # 写入到csv时，不要将索引写入index = False
            self.test.to_csv("test_data.csv", encoding="gbk", index=False)  # 写入到csv时，不要将索引写入index = False
        if method == 'all':
            self.allDivision()
            self.train.to_csv("train_data.csv", encoding="gbk", index=False)  # 写入到csv时，不要将索引写入index = False


# 设置编码
reload(sys)
sys.setdefaultencoding('utf-8')
start =time.clock()
path = u'F:\\postgraduate\\期刊论文\\用户点播信息.xlsx'
div = DivisionTest(path)
# 传入划分方法以及分界线数据，默认前两月为训练集，后两月为测试集
div.saveCSV('all')
end = time.clock()
print u"任务已完成"
print u"完成时长：" + str(end-start)