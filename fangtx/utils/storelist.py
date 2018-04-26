import datetime

# 数据存储：


# 获取表中当天已存在记录
def get_column_list(conn):
    cur = conn.cursor()
    # 获取表中当天已存在的ID
    query = "select detail_url,title from new_house_table where date (store_time) = curdate()"
    flag = cur.execute(query)
    dailys = []
    for daily in cur.fetchmany(flag):
        # daily_info = {
        #     'detail_url': str(daily[0]),
        #     'title': str(daily[1])
        # }
        dailys.append(str(daily[0]))

    return dailys


# 存储新房信息
def store_new_house(items, conn):
    cur = conn.cursor()

    title = items["title"]
    detail_url = items["detail_url"]

    # if detail_url in dailys:
    #     print('该数据已存在： ' + title)
    #     return

    introduce = items["introduce"]
    author = items["author"]
    author_portrait = items["author_portrait"]
    browse = items["browse"]
    label = items["label"]
    issue_time = items["issue_time"]
    store_time = datetime.datetime.now()
    # time = getTimeConversion(issue_time)

    sql = '''
        insert into new_house_table(title,detail_url,introduce,author,author_portrait,browse,label,issue_time,store_time)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s);
       '''
    try:
        cur.execute(sql, (title, detail_url, introduce, author, author_portrait, browse, label, time, store_time))
        conn.commit()
        print('存储完成：' + title)
    except:
        print('存储失败：' + title)

    conn.commit()
    cur.close()

