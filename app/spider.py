# -*- coding: utf-8 -*-
# @Author: chenqiang
# @Date: 2020-07-22 14:08:54

from multiprocessing import Process,Lock
import os,time


def get_spider_task():


    return


def spider_work_process(lock):
    print("start spider process[{}]".os.getpid())
    while True:
        lock.acquire()
        task_lst = get_spider_task()
        if len(task_lst) == 0:
            time.sleep(5)
        lock.release()


def start_spider(process_num = 4):
    lock=Lock()
    for index in range(process_num):
        sp=Process(target=spider_work_process,args=(lock,))
        sp.start()

if __name__ == '__main__':
    init_spider()
    print "end"