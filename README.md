# 电视节目推荐
### 执行程序顺序：
* preTreatment（预处理）：
  * 1.reName.py:将excel中的电视节目提取关键字并重命名
  * 2.Spider.py:从豆瓣爬取相应节目的信息
  * 3.supplement.py:有些数据没有爬下来或者出错了，需要手动纠错，通过此程序手动补充
* model（模型）：
  * 1.DivisionTest.py:划分训练集与测试集，根据要求修改参数
  * 2.compScore.py:加入时间参数和调整系数的模型
  * 3.improCompScore.py:加入调整系数的模型，用于比较
  * 4.oldCompScore.py:原始模型，用于比较
* recommendation（推荐）：
  * （CollaborativeFilter.py和ContentBased.py是协同过滤与基于内容的算法的单独实现，直接用下面的方法即可，无需单独执行）
  * 1.AllRecommendation.py: 利用协同过滤以及基于内容的方法进行离线推荐，并计算准确率（未计算最近邻居个数）
  * 2.HybridRecom.py:实时推荐，利用当前播放的节目类型与接下来要播放的节目信息进行基于内容的推荐
