# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json#########很重要！！不然json.dumps无法运行###################
import pymysql

class Hw2Pipeline(object):
    def __init__(self):
        self.f = open("hw2_pipeline.json","wb")
    def process_item(self, item, spider):
        content = json.dumps(dict(item),ensure_ascii = False) + ", \n"
        self.f.write(content.encode("utf-8"))
        return item
    def close_spider(self,spider):
        self.f.close()

class MysqlPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host = 'localhost', user = 'root', passwd = 'root', db = 'mysql', charset = 'utf8', use_unicode=True)#中文要加utf8#我的mysql密码是root
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        ##############事先在命令行mysql中创建好了一个数据库'homework',指定该数据库进行后续操作###################
        self.cursor.execute("use homework")

        ##############尝试用pymysql在数据库'homework'中创建表格'hw2'。使用smallint小整数型保存数据，占用2字节，更加节约空间#################
        ##############pymysql.err.InternalError: (1074, "Column length too big for column 'bookintro' (max = 16383); use BLOB or TEXT instead")####解决办法：把bookintro的数据类型换成text或blob###
        # self.cursor.execute('create table hw2 (id smallint not null auto_increment, book varchar(200), author varchar(200), bookintro text, latestchapter varchar(2000), updatetime varchar(2000), primary key(id))')


        ##############定义sql语句(插入表格hw2)，方便后面代码不用写这么长######################
        insert_sql = """INSERT INTO hw2(book, author, bookintro, latestchapter, updatetime) VALUES(%s,%s,%s,%s,%s)"""#多行信息用3引号
        try:
            self.cursor.execute(insert_sql, (item['book'], item['author'], item['bookintro'], item['latestchapter'], item['updatetime']))
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
        ##############异常处理，报错内容输出,让它滚回去##############
        return item
    def close_spider(self,spider):
        self.cursor.close()
        self.conn.close()

########另一种存入mysql的方式：异步#########
# from twisted.enterprise import adbapi

# class MysqlPipelineTwo(object):
#     def __init__(self, dbpool):
#         self.dbpool = dbpool
#
#     @classmethod
#     def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
#         """
#         数据库建立连接
#         :param settings: 配置参数
#         :return: 实例化参数
#         """
#         adbparams = dict(
#             host='localhost',
#             db='homework2',
#             user='root',
#             password='root',
#             cursorclass=pymysql.cursors.DictCursor  # 指定cursor类型
#         )
#         # 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
#         dbpool = adbapi.ConnectionPool('pymysql', **adbparams)
#         # 返回实例化参数
#         return cls(dbpool)
#
#     def process_item(self, item, spider):
#         """
#         使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
#         """
#         query = self.dbpool.runInteraction(self.do_insert, item)  # 指定操作方法和操作数据
#         # 添加异常处理
#         query.addCallback(self.handle_error)  # 处理异常
#
#     def do_insert(self, cursor, item):
#         # 对数据库进行插入操作，并不需要commit，twisted会自动commit
#         insert_sql = """insert into hw22222(book, author, bookintro, latestchapter, updatetime) VALUES(%s,%s,%s,%s,%s)"""
#         cursor.execute(insert_sql, (item['book'], item['author'], item['bookintro'], item['latestchapter'], item['updatetime']))
#
#     def handle_error(self, failure):
#         if failure:
#             # 打印错误信息
#             print(failure)

