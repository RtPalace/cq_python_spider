# -*- coding: utf-8 -*-
# @Author: chenqiang
# @Date: 2020-07-22 14:08:54

import pymysql
import sys
import traceback

class DbMysql:
    def __init__(self, conf={'host':'127.0.0.1','port':'3306','user':'root','pwd':'chenqiang','db':'spider','charset':'utf8'}):
        self.host    = conf['host']
        self.port    = conf['port']
        self.user    = conf['user']
        self.pwd     = conf['pwd']
        self.db      = conf['db']
        self.charset = conf['charset']

        self.connection = None
        self.cursor     = None

    def __connect_db(self):
        try:
            self.connection = pymysql.connect(host        = self.host,
                                              user        = self.user,
                                              password    = self.pwd,
                                              db          = self.db,
                                              charset     = self.charset,
                                              cursorclass = pymysql.cursors.DictCursor)
            self.cursor = self.connection.cursor()
            return True
        except:
            raise Exception('数据库连接失败 \n{}'.format(traceback.format_exc()))

    def __close(self):
        if self.connection and self.cursor:
            self.cursor.close()
            self.connection.close()
        return True

    # 执行数据库的sql语句,主要用来做插入、更新、删除操作
    def __execute(self, sql, params=None):
        try:
            # 连接数据库
            self.__connect_db()
            if self.connection and self.cursor:
                # 正常逻辑，执行sql，提交操作
                self.cursor.execute(sql, params)
                self.connection.commit()
                return True
        except:
            self.connection.rollback()
            raise Exception("execute failed:{} params:{}\n{}".format(sql,params,traceback.format_exc()))
        finally:
            self.__close()

    # 批量执行数据库的sql语句,主要用来做插入、更新、删除操作
    def __execute_many(self, sql, params=None):
        try:
            # 连接数据库
            self.__connect_db()
            if self.connection and self.cursor:
                # 正常逻辑，执行sql，提交操作
                self.cursor.executemany(sql, params)
                self.connection.commit()
                return True
        except:
            self.connection.rollback()
            raise Exception("execute many failed:{} params:{}\n{}".format(sql,params,traceback.format_exc()))
        finally:
            self.__close()

    # 批量执行数据库的sql语句,主要用来做插入、更新、删除操作
    def __execute_many_test(self, sql, params=None):
        try:
            # 连接数据库
            self.__connect_db()
            if self.connection and self.cursor:
                # 正常逻辑，执行sql，提交操作
                for info in sql:
                    self.cursor.execute(info, params)
                self.connection.commit()
                return True
        except:
            self.connection.rollback()
            # raise Exception("execute many failed:{} params:{}\n{}".format(sql,params,traceback.format_exc()))
            # print "execute many failed:{} params:{}\n{}".format(sql,params,traceback.format_exc())
            raise Exception("execute many failed:{} \n{}".format(info,traceback.format_exc()))
        finally:
            self.__close()

    # 用来查询表数据
    def __fetchall(self, sql, params=None):
        try:
            # 连接数据库
            self.__connect_db()
            if self.connection and self.cursor:
                self.cursor.execute(sql, params)
                return self.cursor.fetchall()
        except:
            raise Exception("fetchall failed:{} params:{}\n{}".format(sql,params,traceback.format_exc()))
        finally:
            self.__close()

    #增删改查接口
    def query(self, sql, params=None):
        try:
            ret = self.__fetchall(sql, params)
            return ret
        except:
            print ("Query failed:{} params:{} \n{}".format(sql,params,traceback.format_exc()))
            return False

    def insert(self, sql, params=None):
        try:
            ret = self.__execute(sql, params)
            return ret
        except:
            print ("Insert failed:{} params:{} \n{}".format(sql,params,traceback.format_exc()))
            return False

    def delete(self, sql, params=None):
        try:
            ret = self.__execute(sql, params)
            return ret
        except:
            print ("Delete failed:{} params:{} \n{}".format(sql,params,traceback.format_exc()))
            return False

    def update(self, sql, params=None):
        try:
            ret = self.__execute(sql, params)
            return ret
        except:
            print ("Update failed:{} params:{} \n{}".format(sql,params,traceback.format_exc()))
            return False

    #批量增删改接口
    def insert_many(self, sql, params=None):
        try:
            ret = self.__execute_many(sql, params)
            return ret
        except:
            # print ("Insert many failed:{} params:{} \n{}".format(sql,params,traceback.format_exc()))
            print ("Insert many failed:{}  \n{}".format(sql,traceback.format_exc()))
            return False

    #批量增删改接口
    def insert_many_test(self, sql, params=None):
        try:
            ret = self.__execute_many_test(sql, params)
            return ret
        except:
            # print ("Insert many failed:{} params:{} \n{}".format(sql,params,traceback.format_exc()))
            print ("Insert many failed:  \n{}".format(traceback.format_exc()))
            return False

    def delete_many(self, sql, params=None):
        try:
            ret = self.__execute_many(sql, params)
            return ret
        except:
            print ("Delete many failed:{} params:{} \n{}".format(sql,params,traceback.format_exc()))
            return False

    def update_many(self, sql, params=None):
        try:
            ret = self.__execute_many(sql, params)
            return ret
        except:
            print ("Update many failed:{} params:{} \n{}".format(sql,params,traceback.format_exc()))
            return False

if __name__ == "__main__":
    # conf = {'host':'127.0.0.1','port':'3306','user':'root','pwd':'chenqiang','db':'spider','charset':'utf8'}
    # db = DbMysql(conf)
    # sql = "SELECT * FROM novel where id = 1;"
    # print db.query(sql)


    # sql = "update novel set name='hello' where id = 1;"
    # print db.update(sql)

    # sql = "SELECT * FROM novel where id = 1;"
    # print db.query(sql)
    pass
