#-*- coding:utf-8 -*-
# 根据偏好喜爱度模型计算节目评分,不加入时间以及调整系数

import sys
import time
import pandas as pd

class compScore:
    def __init__(self, path):
        self.df = pd.read_csv(path, encoding="gbk")
        # 创建新的dataframe用于存储节目喜爱度
        self.df2 = pd.DataFrame(columns=[u'设备号', u'节目', u'类型', u'完整度', u'喜爱度', u'观看次数'])
        # 创建一个数据字典,用于存放节目信息
        self.proDict = {}

    # 过滤重复的节目，使一个节目只有一个喜爱度
    def delPro(self, row):
        program = self.df.ix[row, u'名称关键字']
        user = self.df.ix[row, u'设备号']
        L = []
        if user in self.proDict:
            if program not in self.proDict[user]:
                self.proDict[user][program] = "true"
                L = self.Compute(row, program, user)
                # print self.proDict
        else:
            self.proDict[user] = {program: "true"}
            L = self.Compute(row, program, user)
        return L

    # 计算节目喜爱度
    def Compute(self, row, program, user):
        userData = self.df[self.df[u'设备号'] == user]
        proData = self.df[self.df[u'名称关键字'] == program]
        data = userData[userData[u'名称关键字'] == program]
        ptimej = float(self.df.ix[row, u'片长'])
        types = self.df.ix[row, u'类型']
        Cij = len(data)
        Cj = len(proData)
        sum_timeij, sum_timej = 0, 0
        # 计算每个节目观看时间与片长的比例的总和
        sum_rate,watch_rates = 0, 0
        for item in data.index:
            ctimeij = float(data.ix[item, u'观看时间'])
            sum_timeij += ctimeij
            sum_rate += ctimeij/ptimej
            watch_rates += ctimeij/ptimej
        for item in proData.index:
            sum_timej += float(proData.ix[item, u'观看时间'])
        # 计算兴趣偏好评分
        Rij = sum_rate/Cij
        #保留前2位
        Rij = float('%.2f' % Rij)
        watch_rate = watch_rates/Cij
        return [user, program, types, watch_rate, Rij, Cij]

    # 将信息保存到df2中
    def saveInfo(self, info=[]):
        new = pd.DataFrame([info], columns=[u'设备号', u'节目', u'类型', u'完整度', u'喜爱度', u'观看次数'])
        self.df2 = self.df2.append(new, ignore_index=True)

    def writeInfo(self):
        for row in self.df.index:
            L = self.delPro(row)
            if L != []:
                self.saveInfo(L)
                print u"正在处理第" + str(row) + u"条记录"
        self.df2.to_csv("train_score.csv", encoding="gbk", index=False)  # 写入到csv时，不要将索引写入index = False


# 设置编码
reload(sys)
sys.setdefaultencoding('utf-8')
start =time.clock()
path = 'train_data.csv'
score = compScore(path)
score.writeInfo()
end = time.clock()
print u"任务已完成"
print u"完成时长：" + str(end-start)