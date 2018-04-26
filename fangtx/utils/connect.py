import pymysql
from pymysql import cursors

#
dbparams = {
    'host': 'XXXXX',
    'port': 3307,
    'user': 'XXXXX',
    'password': 'XXXXX',
    'database': 'fangtx',
    'charset': 'utf8',
    'cursorclass': cursors.DictCursor
}


# 链接数据库，判断是否存在，不存在创建
def connect_net():
    try:
        # 获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
        conn = pymysql.connect(**dbparams)

        cur = conn.cursor()
        # 确定该表是否存在
        query = "show databases like '" + dbparams['database'] + "'"
        flag = cur.execute(query)
        if flag == 0:
            create_db(conn)
        else:
            conn.select_db(dbparams['database'])

    except Exception as e:
        print("数据库链接失败！！" + e)

    return conn


# 创建数据库
def create_db(conn):
    cur = conn.cursor()
    cur.execute('create database if not exists ' + dbparams['database'])
    conn.select_db(dbparams['database'])


#
# 创建数据表
def create_new_house_table(conn):
    cur = conn.cursor()  # 获取一个游标
    # 确定该表是否存在 NewHouse
    query = "show tables like 'new_house_table'"
    flag = cur.execute(query)
    if flag == 0:
        sql = '''
            create table new_house_table(
            id int(11) not null auto_increment primary key,
            province varchar(64) not null,
            city varchar(64) not null,
            community varchar(255) ,
            price varchar(64) ,
            rooms varchar(128) ,
            area varchar(64) ,
            address varchar(128) ,
            district varchar(128) ,
            sale varchar(128) ,
            origin_url varchar(255) ,
            issue_time datetime ,
            store_time datetime ,
            reserved varchar(128) )DEFAULT CHARSET=utf8;
            '''
        cur.execute(sql)


# 创建数据表
def create_esf_house_table(conn):
    cur = conn.cursor()  # 获取一个游标
    # 确定该表是否存在
    query = "show tables like 'esf_house_table'"
    flag = cur.execute(query)
    if flag == 0:
        sql = '''
            create table esf_house_table(
            id int(11) not null auto_increment primary key,
            province varchar(64) not null,
            city varchar(64) not null,
            community varchar(255) ,
            price varchar(64) ,
            unit varchar(128) ,
            rooms varchar(128) ,
            area varchar(64) ,
            address varchar(128) ,
            district varchar(128) ,
            sale varchar(128) ,
            floor varchar(128) ,
            toward varchar(128) ,
            construct varchar(128) ,
            origin_url varchar(255) ,
            issue_time datetime ,
            store_time datetime ,
            reserved varchar(128) )DEFAULT CHARSET=utf8;
            '''
        cur.execute(sql)


def create_table():
    create_new_house_table(connect_net())
    create_esf_house_table(connect_net())

#
# create_table()

# dbparams = {
#            'host': '127.0.0.1',
#            'port': 3306,
#            'user': 'root',
#            'password': 'root',
#            'database': 'jianshu2',
#            'charset': 'utf8',
#            'cursorclass': cursors.DictCursor
#        }
#        # 数据库连接池
#        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
#        self._sql = None
