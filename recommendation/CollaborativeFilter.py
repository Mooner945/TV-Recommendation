#-*- coding:utf-8 -*-
# 协同过滤推荐

import sys
import time
import pandas as pd

class CollaborativeFilter:
    def __init__(self, path1, path2, path3):
        table_name = [u'设备号', u'节目', u'喜爱度']
        self.rate = pd.read_csv(path3, encoding="gbk", usecols=table_name)
        self.te = pd.read_csv(path2, encoding="gbk")
        # 将集合进行排序
        self.row_tr = sorted(list(set(self.rate[u'设备号'])))  # 用户集合
        self.col_tr = sorted(list(set(self.rate[u'节目'])))  # 物品集合

    # 余弦相似度
    def cosine(self, x, y):
        # 分母
        denominator = (sum(x * x) * sum(y * y)) ** 0.5
        try:
            value = sum(x * y) / denominator
        except ZeroDivisionError:
            value = 0
        return value

    # 计算用户矩阵
    def computeUser(self):
        # 转换成User-Item矩阵
        df = self.rate.pivot(index=u'设备号', columns=u'节目', values=u'喜爱度')
        df = df.fillna(0)
        # 构建用户相似度矩阵
        self.userdf = pd.DataFrame(0, index=self.row_tr, columns=self.row_tr)
        m = 0
        for i in self.row_tr:
            for j in self.row_tr:
                if j > i:
                    x = df.loc[i]
                    y = df.loc[j]
                    self.userdf.loc[i, j] = float('%.4f' % self.cosine(x, y))
                    self.userdf.loc[j, i] = self.userdf.loc[i, j]
            # m += 1
            # print u"正在计算第" + str(m) + u"条记录"
        # self.userdf.to_csv("user_matrix.csv", encoding="gbk", index=True)

    # 计算物品矩阵
    def computeItem(self):
        # 转换成Item-User矩阵
        df2 = self.rate.pivot(index=u'节目', columns=u'设备号', values=u'喜爱度')
        df2 = df2.fillna(0)
        # 构建物品相似度矩阵
        self.itemdf = pd.DataFrame(0, index=self.col_tr, columns=self.col_tr)
        m = 0
        for i in self.col_tr:
            for j in self.col_tr:
                if j > i:
                    x = df2.loc[i]
                    y = df2.loc[j]
                    self.itemdf.loc[i, j] = float('%.4f' % self.cosine(x, y))
                    self.itemdf.loc[j, i] = self.itemdf.loc[i, j]
            # m += 1
            # print u"正在计算第" + str(m) + u"条记录"
        self.itemdf.to_csv("item_matrix.csv", encoding="gbk", index=True)

    # 获得所有给用户推荐的节目，按推荐度从大到小排序
    def userRecommend(self):
        # self.userdf = pd.read_csv("user_matrix.csv", encoding="gbk", index_col=0)
        # 存放已排序的推荐节目
        S = {}
        for i in self.userdf.index:
            # 获取用户已经观看的节目信息
            ui = self.rate[self.rate[u"设备号"] == i]
            userdata = set(ui[u"节目"])
            # 存放已经预测喜爱度的节目
            pro_set = {}
            for j in self.userdf.index:
                # 如果uj比ui小，则不计算
                if j != i:
                    # 获得用户矩阵中i和j的用户相似度
                    distance = self.userdf.loc[i, j]
                    if distance != 0:
                        # 获得设备号为j的所有用户信息
                        neighbor_user = self.rate[self.rate[u"设备号"] == j]
                        for k in neighbor_user.index:
                            rating = neighbor_user.loc[k, u'喜爱度']
                            pro = neighbor_user.loc[k, u'节目']
                            # 如果节目已经被用户观看，那么不推荐
                            if pro not in userdata:
                                rec_score = distance*rating
                                rec_score = float('%.4f' % rec_score)
                                # 如果节目已预测，那么选择评分高的作为推荐度
                                # 如果节目没预测，将此节目以及推荐度加入已预测节目字典
                                if pro in pro_set:
                                    if rec_score > pro_set[pro]:
                                        pro_set[pro] = rec_score
                                else:
                                    pro_set[pro] = rec_score
            # 对节目推荐度进行排序
            pro_sort = sorted(pro_set.items(), key=lambda l: l[1], reverse=True)
            S[i] = pro_sort
        return S

    # 获得所有给用户推荐的节目，按推荐度从大到小排序
    def itemRecommend(self):
        # self.itemdf = pd.read_csv("item_matrix.csv", encoding="gbk", index_col=0)
        # 存放已排序的推荐节目
        S = {}
        for i in self.row_tr:
            # 获取用户已经观看的节目信息
            ui = self.rate[self.rate[u"设备号"] == i]
            userdata = ui[u"节目"]
            # 存放已经预测喜爱度的节目
            pro_set = {}
            for j in userdata:
                pj = ui[ui[u"节目"] == j]
                rating = pj[u'喜爱度']
                for k in self.col_tr:
                    # 节目相同则不计算
                    if j != k:
                        distance = self.itemdf.loc[j, k]
                        if distance != 0:
                            # 如果节目已经被用户观看，那么不推荐
                            if k not in userdata:
                                rec_score = distance*rating
                                rec_score = float('%.4f' % rec_score)
                                # 如果节目已预测，那么选择评分高的作为推荐度
                                # 如果节目没预测，将此节目以及推荐度加入已预测节目字典
                                if k in pro_set:
                                    if rec_score > pro_set[k]:
                                        pro_set[k] = rec_score
                                else:
                                    pro_set[k] = rec_score
            # 对节目推荐度进行排序
            pro_sort = sorted(pro_set.items(), key=lambda l: l[1], reverse=True)
            S[i] = pro_sort
        return S

    # 选择前m个节目作为评价
    def selectM(self, S={}, m=10, method='user'):
        # 构建用于储存推荐信息的dataframe
        self.rec = pd.DataFrame(columns=[u'设备号', u'节目', u'推荐度'])
        for i in self.row_tr:
            pro_sort = S[i]
            like_pros = pro_sort[0:m]
            L = []
            for item in like_pros:
                L.append([i, item[0], item[1]])
            # 将用户i的推荐信息写入到推荐数据
            new = pd.DataFrame(L, columns=[u'设备号', u'节目', u'推荐度'])
            self.rec = self.rec.append(new, ignore_index=True)
            # print u"正在给" + str(i) + u"号用户推荐"
        # if method == 'user':
        #     self.rec.to_csv("user_result.csv", encoding="gbk", index=False)
        # elif method == 'item':
        self.rec.to_csv("item_result.csv", encoding="gbk", index=False)

    # 利用准确率和召回率来评价
    def evaluation(self):
        RU, TU, RTU = 0,0,0
        for i in self.row_tr:
            T = self.te[self.te[u"设备号"] == i]
            R = self.rec[self.rec[u"设备号"] == i]
            if T.notnull:
                t = T[u'名称关键字']
                r = R[u'节目']
                Tu = len(t)
                T_set = set(t)
                Ru = len(r)
                RTu = float(0)
                for pro in r:
                    if pro in T_set:
                        RTu += 1
                RU += Ru
                TU += Tu
                RTU += RTu
        # print RTU
        # print TU
        # print RU
        precision = RTU/RU
        precision = float('%.4f' % precision)
        recall = RTU/TU
        recall = float('%.4f' % recall)
        return [precision,recall]

    # 主程序，输入协同过滤方法，距离计算方法，推荐m个节目
    def main(self):
        pre_df = pd.DataFrame(columns=['K', 'User-based', 'Item-based'])
        rec_df = pd.DataFrame(columns=['K', 'User-based', 'Item-based'])
        self.computeUser()
        self.computeItem()
        S1 = self.userRecommend()
        S2 = self.itemRecommend()
        for m in range(1, 11):
            self.selectM(S1, m)
            print u"正在计算user-based m=" + str(m) + u"的准确率与召回率"
            L1 = self.evaluation()
            self.selectM(S2, m)
            print u"正在计算item-based m=" + str(m) + u"的准确率与召回率"
            L2 = self.evaluation()
            # print L
            pre = [m, L1[0], L2[0]]
            rec = [m, L1[1], L2[1]]
            new1 = pd.DataFrame([pre], columns=['K', 'User-based', 'Item-based'])
            new2 = pd.DataFrame([rec], columns=['K', 'User-based', 'Item-based'])
            pre_df = pre_df.append(new1, ignore_index=True)
            rec_df = rec_df.append(new2, ignore_index=True)
        pre_df.to_csv("precision.csv", encoding="gbk", index=False)
        rec_df.to_csv("recall.csv", encoding="gbk", index=False)

# 设置编码
reload(sys)
sys.setdefaultencoding('utf-8')
start =time.clock()
path1 = 'train_data.csv'
path2 = 'test_data.csv'
path3 = 'train_score.csv'
cf = CollaborativeFilter(path1, path2, path3)
# cf.main()
cf.computeItem()
cf.selectM(cf.itemRecommend(), 10)
end = time.clock()
print u"任务已完成"
print u"完成时长：" + str(end-start)










