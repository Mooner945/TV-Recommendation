#-*- coding:utf-8 -*-
# 节目信息有的匹配不成功，手动输入网址，下载内容
# 每次只需要修改row行号和url网页地址

import sys
import openpyxl
import requests
import re
from requests.exceptions import ReadTimeout,ConnectionError,RequestException
import time
from bs4 import BeautifulSoup

class Spider:
    def __init__(self, path, sheet):
        self.path = path
        self.sheet = sheet
        # 节目名称列号
        self.proCol = 1
        # 打开文件
        self.data = openpyxl.load_workbook(path)
        # 打开需要操作的sheet
        self.sheet_name = self.data[sheet]
        self.n_of_rows = self.sheet_name.max_row  # 获取行号
        #定义需要采集的信息内容
        self.director = u"导演"
        self.screenwriter = u"编剧"
        self.actors = u"主演"
        self.types = u"类型"
        self.area = u"制片"
        self.language = u"语言"
        self.duration = u"片长"
        self.episode = u"集数"
        self.introduction = u"简介"
        self.name = u"名称"
        self.year = u"年份"
        self.rating = u"评分"
        self.num = u"评价人数"
        self.pic = u"图片"

    #根据网址
    def getInfo(self,url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        # proxies = {
        #     "https": "http://119.28.194.66:8888","https": "http://115.198.38.58:6666","https": "http://180.118.240.12:61234",
        #     "https": "http://121.61.89.38:61234","https": "http://112.67.32.246:8118","https": "http://111.76.137.119:808"
        # }
        sleep_download_time = 10
        # 先将键值初始化
        director_value, screenwriter_value, actors_value, types_value, area_value, language_value = "", "", "", "", "", ""
        duration_value, episode_value, introduction_value, rating_value, num_value, year_value = "", "", "", "", "", ""
        pic_value, name_value, info = "", "", ""
        try:
            #time.sleep(sleep_download_time)
            response = requests.get(url, headers=headers)
            page = response.text
            soup = BeautifulSoup(page, "lxml")
            if soup.find('div', {'id': 'info'}):
                info = soup.find('div', {'id': 'info'}).text
                words = re.split('[\t\n\r]', info)
                for word in words:
                    if self.director in word:
                        key = re.split('[:]', word)
                        director_value = key[1].encode("gbk", "ignore")
                        continue
                    elif self.screenwriter in word:
                        key = re.split('[:]', word)
                        screenwriter_value = key[1].encode("gbk", "ignore")
                        continue
                    elif self.actors in word:
                        key = re.split('[:]', word)
                        actors_value = key[1].encode("gbk", "ignore")
                        continue
                    elif self.types in word:
                        key = re.split('[:]', word)
                        types_value = key[1].encode("gbk", "ignore")
                        continue
                    elif self.area in word:
                        key = re.split('[:]', word)
                        area_value = key[1].encode("gbk", "ignore")
                        continue
                    elif self.language in word:
                        key = re.split('[:]', word)
                        language_value = key[1].encode("gbk", "ignore")
                        continue
                    elif self.duration in word:
                        # 找到时长参数里面的数字部分，多个时长只取第一个
                        duration_value = re.findall(r"\d+", word)[0]
                        continue
                    elif self.episode in word:
                        key = re.split('[:]', word)
                        episode_value = key[1].encode("gbk", "ignore")
                        continue
            if soup.find('span', {'property': 'v:itemreviewed'}):
                name_value = soup.find('span', {'property': 'v:itemreviewed'}).text.encode('gbk', 'ignore')
            if soup.find('span', {'class': 'year'}):
                year_value = re.findall(r"\d+", soup.find('span', {'class': 'year'}).text)[0]
            if soup.find('span', {'property': 'v:summary'}):
                introduction_value = soup.find('span', {'property': 'v:summary'}).text.encode('gbk', 'ignore')
            if soup.find('strong', {'property': 'v:average'}):
                rating_value = soup.find('strong', {'property': 'v:average'}).text
            if soup.find('span', {'property': 'v:votes'}):
                num_value = soup.find('span', {'property': 'v:votes'}).text.encode('gbk', 'ignore')
            if soup.find('img', {'rel': 'v:image'}):
                pic_value = soup.find('img', {'rel': 'v:image'}).get('src')
        except ReadTimeout:
            print("timeout")
        except ConnectionError:
            print("connection Error")
        except RequestException:
            print("error")

        return [name_value,year_value,introduction_value,rating_value,num_value,director_value,screenwriter_value,
                actors_value,area_value,language_value,duration_value,episode_value,types_value,pic_value]

    def saveInfo(self, row, url):
        col = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        col_num = len(col)
        l = self.getInfo(url)
        for item in range(col_num):
            self.sheet_name[col[item] + str(row)] = l[item].lstrip().rstrip().decode('gbk')
        print l[0]
        print u"补充第" + str(row) + u"条记录完成"
        self.data.save(self.path)

# 设置编码
reload(sys)
sys.setdefaultencoding('utf-8')
start =time.clock()
path = u'F:\\postgraduate\\期刊论文\\节目信息.xlsx'
sheet = u"Sheet1"
spider = Spider(path, sheet)
#需要补充的行和网页地址
row = 663
url = "https://movie.douban.com/subject/27001400/"
spider.saveInfo(row, url)
end = time.clock()
print u"任务已完成"
print u"完成时长：" + str(end-start)