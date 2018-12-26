

import os,conf



def log_append(var):
    if conf.itadmin_debug:
        print("log#]" + var)

def log_sql_append(var):
    if conf.itadmin_debug:
        print("log_sql#]" + var)
        pass