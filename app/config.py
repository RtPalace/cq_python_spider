# -*- coding: utf-8 -*-
# @Author: chenqiang
# @Date: 2020-07-22 14:08:54

import os
from time import strftime

# 用于存放数据
BASE_PATH = os.path.join(os.getcwd(), 'data')
# 日志文件
LOG_FILE = os.path.join(BASE_PATH, 'xiaoshuo.log')
# 用于存放爬取状态，可用于断点爬取
LOG_STAT = os.path.join(BASE_PATH, 'spider_state.json')
# 豆瓣电影分类文件
MOVIES_TYPE_FILE = os.path.join(BASE_PATH, 'movies_type.csv')


# 顶点小说网
DDXS_URL = "https://www.ddxs.cc"

# 新笔趣网
XBQW_URL = "http://www.xbiqukan.com/"
XBQW_SEARCH_URL = "http://www.xbiqukan.com/search.html?searchtype=novelname&searchkey="

# 日志文件
LOG_DIR = os.path.join(BASE_PATH, 'log')
LOGGER_FILE = os.path.join(LOG_DIR, 'info_{}.log'.format(strftime('%Y%m%d')))
LOGGER_ERROR_FILE = os.path.join(LOG_DIR, 'error_{}.log'.format(strftime('%Y%m%d')))

if not os.path.exists(BASE_PATH):
    os.mkdir(BASE_PATH)

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)



#抓取小说的列表：
SPIDER_NOVELS =  ["诸天大道宗","龙蛇演义","凡人修仙传","大道争锋","无限道武者路","武侠江湖大冒险","诸天演道","剑出华山","无限修仙", "宅在诸天万界", "武侠世界大冒险"]

