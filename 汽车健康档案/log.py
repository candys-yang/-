

import os,conf,sqlite3,datetime



def log_append(var):
    if conf.itadmin_debug:
        print("log#]" + str(var))
    if conf.itadmin_log:
        sqlconn = sqlite3.connect('datebase.db')
        sqlcmd = sqlconn.cursor()
        sqlcmd.executemany("INSERT INTO [softlog] VALUES (?,?)",[(datetime.datetime.now(),str(var))])
        sqlconn.commit()
        pass

def log_sql_append(var):
    if conf.itadmin_debug:
        print("log_sql#]" + str(var))
        pass