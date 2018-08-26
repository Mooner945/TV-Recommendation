#-*- coding:utf-8 -*-
# 基于内容的推荐

import sys
import time
import pandas as pd


class ContentBased:
    def __init__(self, path1, path2, path3):
        table_name = [u'设备号', u'名称关键字', u'制片', u'语言', u'类型']
        self.tr = pd.read_csv(path1, encoding="gbk", usecols=table_name)
        self.te = pd.read_csv(path2, encoding="gbk", usecols=table_name)
        rate_name = [u'设备号', u'节目', u'喜爱度']
        self.rate = pd.read_csv(path3, encoding="gbk", usecols=rate_name)
        self.all = pd.DataFrame(columns=table_name)
        self.all = self.all.append(self.tr, ignore_index=True)
        self.all = self.all.append(self.te, ignore_index=True)
        self.all_tr = sorted(list(set(self.all[u'名称关键字'])))  # 节目集合
        self.row_tr = sorted(list(set(self.tr[u'设备号'])))  # 训练集用户集合

    # 建立物品-属性矩阵
    def createAttr(self):
        col_tr = set()  #属性集合
        for i in self.all.index:
            production = self.all.loc[i, u'制片'].strip().split('/')
            language = self.all.loc[i, u'语言'].strip().split('/')
            genre = self.all.loc[i, u'类型'].strip().split('/')
            for p in production:
                col_tr.add(p)
            for l in language:
                col_tr.add(l)
            for g in genre:
                col_tr.add(g)
        # 构建物品-属性矩阵
        self.contentdf = pd.DataFrame(0, index=self.all_tr, columns=col_tr)
        for item in self.all_tr:
            pro = self.all[self.all[u"名称关键字"] == item]
            # 将每个属性的值取出，按/分割开来
            a = list(set(pro[u"制片"]))
            a_list = a[0].strip().split('/')
            b = list(set(pro[u"语言"]))
            b_list = b[0].strip().split('/')
            c = list(set(pro[u"类型"]))
            c_list = c[0].strip().split('/')
            # 将节目拥有的制片、语言、类型写为1
            for o in a_list:
                self.contentdf.loc[item, o] = 1
            for p in b_list:
                self.contentdf.loc[item, p] = 1
            for q in c_list:
                self.contentdf.loc[item, q] = 1
        # self.contentdf.to_csv("content_matrix.csv", encoding="gbk", index=True)

    # 余弦相似度
    def cosine(self, x, y):
        # 分母
        denominator = (sum(x * x) * sum(y * y)) ** 0.5
        try:
            value = sum(x * y) / denominator
        except ZeroDivisionError:
            value = 0
        return value

    # 建立物品相似度矩阵
    def computeContent(self):
        # self.contentdf = pd.read_csv('content_matrix.csv', encoding="gbk", index_col=0)
        # 构建物品相似度矩阵
        self.allitemdf = pd.DataFrame(0, index=self.all_tr, columns=self.all_tr)
        m = 0
        for i in self.all_tr:
            for j in self.all_tr:
                if j > i:
                    x = self.contentdf.loc[i]
                    y = self.contentdf.loc[j]
                    self.allitemdf.loc[i, j] = float('%.4f' % self.cosine(x, y))
                    self.allitemdf.loc[j, i] = self.allitemdf.loc[i, j]
            m += 1
            # print u"正在计算第" + str(m) + u"条记录"
        # self.allitemdf.to_csv("item_matrix.csv", encoding="gbk", index=True)

    # 进行推荐
    def recommend(self):
        # self.allitemdf = pd.read_csv('item_matrix.csv', encoding="gbk", index_col=0)
        # 创建存放已排序的字典
        S = {}
        # 待推荐的节目列表
        pro_set = set(self.te[u"名称关键字"])
        for i in self.row_tr:
            u = self.rate[self.rate[u'设备号'] == i]
            # 用户ui观看的节目集合
            pro = u[u'节目']
            # 建立节目相似度字典
            pro_dict = {}
            for j in pro:
                v = u[u[u"节目"] == j]
                rating = v[u"喜爱度"]
                for k in self.all_tr:
                    if k not in pro:
                        if k in pro_set:
                            sim = self.allitemdf.loc[j, k]
                            pred = sim*rating
                            pred = float('%.2f' % pred)
                            if pred != 0:
                                # 如果节目已预测，那么选择评分高的作为推荐度
                                # 如果节目没预测，将此节目以及推荐度加入已预测节目字典
                                if k in pro_dict:
                                    if pred > pro_dict[k]:
                                        pro_dict[k] = pred
                                else:
                                    pro_dict[k] = pred
                                    # 对节目推荐度进行排序
            pro_sort = sorted(pro_dict.items(), key=lambda l: l[1], reverse=True)
            S[i] = pro_sort
        return S

    # 选择前m个节目作为评价
    def selectM(self, S={}, m=10):
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
        # self.rec.to_csv("item_result.csv", encoding="gbk", index=False)

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
        pre_df = pd.DataFrame(columns=['K', 'Content-based'])
        rec_df = pd.DataFrame(columns=['K', 'Content-based'])
        self.createAttr()
        self.computeContent()
        S = self.recommend()
        for m in range(1, 11):
            self.selectM(S, m)
            print u"正在计算content-based m=" + str(m) + u"的准确率与召回率"
            L = self.evaluation()
            print L
            pre = [m, L[0]]
            rec = [m, L[1]]
            new1 = pd.DataFrame([pre], columns=['K', 'Content-based'])
            new2 = pd.DataFrame([rec], columns=['K', 'Content-based'])
            pre_df = pre_df.append(new1, ignore_index=True)
            rec_df = rec_df.append(new2, ignore_index=True)
        pre_df.to_csv("precision.csv", encoding="gbk", index=False)
        rec_df.to_csv("recall.csv", encoding="gbk", index=False)


# 设置编码
reload(sys)
sys.setdefaultencoding('utf-8')
start =time.clock()
path1 = 'F:\\python-save\\myPaper\\model\\train_data.csv'
path2 = 'F:\\python-save\\myPaper\\model\\test_data.csv'
path3 = 'F:\\python-save\\myPaper\\model\\train_score.csv'
con = ContentBased(path1, path2, path3)
con.main()
end = time.clock()
print u"任务已完成"
print u"完成时长：" + str(end-start)