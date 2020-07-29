# -*- coding: utf-8 -*-
# @Author: chenqiang
# @Date: 2020-07-22 14:08:54

import os
import time
import requests
from bs4 import BeautifulSoup                   # pip install bs4
from pymysql.err import ProgrammingError        # pip install PyMySQL
from spider_tools import get_one_page
from config import XBQW_URL,BASE_PATH,SPIDER_NOVELS
import sys
import traceback

from db import DbMysql
reload(sys)
sys.setdefaultencoding('utf8')

from multiprocessing import Process,Lock

def search_all_novel(name,flag=0):
    """
    输入小说名字
    返回小说在网站的具体网址
    """
    if name is None:
        raise Exception('请输入小说名字！！！')
    url = '{}search.html?searchtype=novelname&searchkey={}'.format(XBQW_URL,name)
    html = get_one_page(url, sflag=flag)
    soup = BeautifulSoup(html,"html.parser")

    result_list = soup.find(id="newscontent")
    result_list = result_list.find(class_ = 'l')
    novel_lst = result_list.find_all('li')

    novels = []
    for novel in  novel_lst:
        novel_info_1 = novel.find(class_ = 's2').find('a')
        novel_info_2 = novel.find(class_ = 's5')

        novel_name = novel_info_1.string
        novel_url = "{}{}".format(XBQW_URL,novel_info_1['href'])
        novel_author = novel_info_2.string

        novel_info = {"name":novel_name,"url":novel_url,"author":novel_author}
        novels.append(novel_info)

    if [] == novels:
        raise Exception('{} 小说不存在！！！'.format(name))
    return novels

def search_novel(name,flag=0):
    '''
    按书名或作者名搜索，返回完全匹配或搜索到的第一个小说
    '''
    novels = search_all_novel(name,flag)
    if novels == []:
        raise Exception('{} 小说不存在！！！'.format(name))
    else:
        names = [info['name'] for info in novels]
        authors = [info['author'] for info in novels]

        novel_info = None
        if name in names:
            for info in novels:
                if name == info['name']:
                    novel_info = info
        elif name in authors:
            for info in novels:
                if name == info['author']:
                    novel_info = info
        else:
            # novel_info = novels[0]
            raise Exception('{} 小说不存在！！！'.format(name))

        if None == novel_info:
            raise Exception('{} 小说不存在！！！'.format(name))
        else:
            return novel_info

def get_novel_chapter_info(novel_info, flag=1):
    '''
    获取小说列表
    '''
    novel_name = novel_info['name']
    novel_url = novel_info['url']

    print "获取小说{}列表".format(novel_name)
    novel_html = get_one_page(novel_url, sflag=flag)
    soup = BeautifulSoup(novel_html,"html.parser")

    head = soup.find('head')
    author = head.find(property = "og:novel:author")['content']
    updatetime = head.find(property = "og:novel:update_time")['content']
    new_chapter = head.find(property = "og:novel:latest_chapter_name")['content']
    dd_lst = soup.find('dl').find_all('a')
    novel_chapter_lst = [{"name":info.string,"url":"{}{}".format(XBQW_URL,info['href'])} for info in dd_lst]
    novel_chapter_num = len(novel_chapter_lst)
    novel_chapter_info = {'novel_name':novel_name,'author':author,'new_chapter':new_chapter,'updatetime':updatetime,'chapter_number':novel_chapter_num,'chapters':novel_chapter_lst}
    return novel_chapter_info

def get_chapter_content(chapter_name, chapter_url, flag=1):
    html = get_one_page(chapter_url, sflag=flag)
    soup = BeautifulSoup(html,"html.parser")
    chapter_content = soup.find(class_ = 'content_read').find('div',id = 'content').text
    chapter_content = "{}{}".format(chapter_name,chapter_content)
    return chapter_content


def save_novel(name,chapter_info):
    save_novel_file = "{}.txt".format(name)
    print save_novel_file

    with open(save_novel_file,"wb") as f:
        for chapter in chapter_info['chapters']:
            chapter_name = chapter['name']
            chapter_url = chapter['url']
            print "下载{}".format(chapter_name)
            chapter_content = get_chapter_content(chapter_name, chapter_url)
            print "保存{}".format(chapter_name)
            f.write(chapter_content)
        print "小说{}保存完成".format(name)


def get_novel_task(lock):
    try:
        lock.acquire() #枷锁
        db = DbMysql()
        novel_task_sql_str = "SELECT * FROM novel_task WHERE status = 0 LIMIT 1;"
        novel_task_ret = db.query(novel_task_sql_str)
        if () == novel_task_ret:
            return False
        update_novel_task_sql_str = "UPDATE novel_task SET status = 1 where id={};".format(novel_task_ret[0]['id'])
        db.update(update_novel_task_sql_str)
        return novel_task_ret
    except:
        print "获取小说任务失败\n{}".format(traceback.format_exc())
        return False
    finally:
        lock.release() #解锁



def download_spider_task(lock,task_lst):
    db = DbMysql()
    for task in task_lst:
        try:
            chapter_content = get_chapter_content(task["chapter_name"], task["spider_url"])
            novel_path = "{}/{}".format(BASE_PATH,task["novel_name"])
            if not os.path.exists(novel_path):
                os.mkdir(novel_path)
            task["chapter_name"] = task["chapter_name"].replace('/','|')
            novel_chapter_save_file = "{}/{}_{}.txt".format(novel_path,task["chapter_id"],task["chapter_name"])
            print novel_chapter_save_file
            with open(novel_chapter_save_file,"wb") as cf:
                cf.write(chapter_content)
                print "下载小说{}章节{}，保存为{}".format(task["novel_name"],task["chapter_name"],novel_chapter_save_file)


                lock.acquire() #枷锁
                update_novel_task_sql_str = "UPDATE novel_task SET status = 2 where id={};".format(task['id'])
                db.update(update_novel_task_sql_str)
                lock.release() #解锁
        except:
            print "获取小说任务失败\n{}".format(traceback.format_exc())
            lock.acquire() #枷锁
            update_novel_task_sql_str = "UPDATE novel_task SET status = 3 , repeat_num = 1 where id={};".format(task['id'])
            db.update(update_novel_task_sql_str)
            lock.release() #解锁
            # return False


def spider_work_process(lock):
    print('spider process %s is running' %os.getpid())
    while 1:
        novel_task = get_novel_task(lock)
        if False == novel_task:
            time.sleep(5)
            continue
        download_spider_task(lock,novel_task)
        time.sleep(0.1)

def create_novel_tasks(lock):
    try:
        lock.acquire() #枷锁

        db = DbMysql()
        task_sql_str = "SELECT id,name,search_url FROM task where status = 0 and type = 0;"
        task_sql_ret = db.query(task_sql_str)

        for task_info in task_sql_ret:
            task_id =  task_info['id']
            name = task_info['name']
            url = task_info['search_url']
            novel_chapter_info = get_novel_chapter_info({'name':name,"url":url})
            author = novel_chapter_info['author']
            updatetime = novel_chapter_info['updatetime']

            #增加novel_task记录
            novel_task_sql_str = "INSERT INTO novel_task (task_id,chapter_id, novel_name, chapter_name,author,novel_update_time, status, repeat_num, spider_url, create_time, update_time) VALUES (%s, %s,%s, %s,%s, %s, 0, 0, %s, NOW(), NOW());"
            
            # novel_chapter_data = [(str(task_id),name,info['name'],author,updatetime,info['url']) for info in novel_chapter_info['chapters']]
            i = 0
            novel_chapter_data = []
            for info in novel_chapter_info['chapters']:
                i = i+1
                data = (str(task_id),str(i),name,info['name'],author,updatetime,info['url'])
                novel_chapter_data.append(data)

            db.insert_many(novel_task_sql_str,novel_chapter_data)

            #修改task记录
            modify_task_sql_str = "UPDATE task SET status = 1 where id={} and name='{}';".format(task_id,name)
            db.update(modify_task_sql_str)
            return True
    except:
        print "create novel task falied:{}".format(traceback.format_exc())
        return False
    finally:
        lock.release() #解锁

def task_process(lock):
    print('task process %s is running' %os.getpid())
    while True:
        create_novel_tasks(lock)
        time.sleep(5)

def add_novel_task(novel_name):
    try:
        novel_info = search_novel(novel_name)
        #创建小说任务
        db = DbMysql()
        query_task_sql = "SELECT id FROM task where name = '{}' and type = 0;".format(novel_info['name'])
        query_ret = db.query(query_task_sql)
        if () == query_ret:
            task_sql = "INSERT INTO task (name, type, status,search_url,create_time, update_time, error_info) VALUES ('{}', 0, 0,'{}', NOW(), NOW(), NULL);".format(novel_info['name'],novel_info['url'])
            db.insert(task_sql)
        else:
            err_info = "数据库中task已有:name={} type=0".format(novel_info['name'])
            print err_info
            return False, err_info
        return True
    except:
        err_info = "{}".format(traceback.format_exc())
        print err_info
        return False, err_info

def run():
    #创建锁
    lock = Lock()

    #开启爬虫进程
    process_num = 8
    for index in range(process_num):
        sp=Process(target=spider_work_process,args=(lock,))
        sp.start()

    #开启任务刷新进程
    tp=Process(target=task_process,args=(lock,))
    tp.start()

    # 添加爬虫任务
    for name in SPIDER_NOVELS:
        add_novel_task(name)

if __name__ == "__main__":
    run()
    # search_novel("凡人修仙传")