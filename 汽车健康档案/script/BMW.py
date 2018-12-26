#coding=utf-8

'''

    该文件是解析dms导出的数据文件并结构化数据
    配置项遵循 python 语法标准。

    日期：2018-12-14   作者：杨主任
    Email： 522703331@qq.com 
    GIT：https://github.com/candys-yang/
    blog：http://varmain.com

    ##################################################
    [2018-12-14]:
        在大部分情况下，你不必更改该文件的任何代码与参数。
        该模块的已知缺陷和风险：
            -> 由于宝马的 Kprint 输出的数据文件编码问题，导
               致了字符位置存在偏差。
            -> 如果数据项有更多的中文字符，可能会产生数据
               溢出，这将导致生成的最终数据非常不准确。
            -> 配件信息的数据非常不稳定，因此采用简易的数据
               算法来提取数据。

'''


import os,conf,log
import sqlite3 as sql
import uuid

#全局唯一标识符，用于标识数据库记录
bmw_guid = uuid.uuid1()

log.log_append("Load BMW.py")
log.log_append("import BMW.py UUID: " + str(bmw_guid))
#数据参数,若不确定这些模块参数的作用，请勿更改它
bmw_base_dealerid = [1,6]    
bmw_base_invocieid = [7,13]
bmw_base_chassisno = [36,53]
bmw_base_regno = [54,73]
bmw_base_orderdate = [74,84]
bmw_base_mileage = [86,94]
bmw_base_orderno = [95,108]
bmw_base_invoicedate = [125,135]
bmw_labor_dealerid = [1,6]
bmw_labor_invoiceid = [7,13]
bmw_labor_wipno = [14,19]
bmw_labor_itemcode = [27,47]
bmw_labor_description = [48,78]
bmw_labor_qty = [79,92]
bmw_labor_unit = [93,95]
bmw_labor_txtdescription = [96,200]
bmw_parts_dealerid = [1,6]
bmw_parts_invoiceid = [7,13]
bmw_parts_wipno = [14,19]
bmw_parts_itemcode = [27,47]
bmw_parts_description = [48,78]
bmw_parts_qty = [78,92]



# ----------------------- 预处理指令 ------------------
# 扫描目录文件
bmw_datafile = []       #数据文件列表
bmw_filetext = []
try:
    for col in os.listdir(conf.mod_parameters[0]):
        bmw_datafile.append(col)
except :
    log.log_append("['ERROR','BMW.py','scan dir ','" + conf.mod_parameters[0] +"']")

#------------------------------------------------------

#读取所有数据文件内容
def readfile(filename):
    f = open(filename)
    title_cursor = 0    #for 计数器
    datatype = ""
    dataread = False
    log.log_append("---------- BMW.py: readfile() "+ filename +"  ------------")
    CurrerLineStrSumLABOR = []  #日志用
    for line in f.readlines():
        title_cursor += 1
        #寻找页头
        if line.find("- HEADR (SO) --") >= 1:
            datatype = "HEADR" 
            dataread = True
        elif line.find("- LABOR (SO) --") >= 1:
            datatype = "LABOR" 
            dataread = True
        elif line.find("Parts (SO) --") >= 1:
            datatype = "Parts" 
            dataread = True
        pass
        #提取有用行信息
        if datatype=="HEADR" and dataread and line.find(conf.dealer_id) >= 1:
            headr = []
            headr.append(  line[bmw_base_dealerid[0]:bmw_base_dealerid[1]]  )
            headr.append(  line[bmw_base_invocieid[0]:bmw_base_invocieid[1]]  )
            headr.append(  line[bmw_base_chassisno[0]:bmw_base_chassisno[1]]  )
            #如果出现空车牌，数据会溢出，因此，这里采用数据算法处理数据
            regnotxt = line[bmw_base_regno[0]:bmw_base_regno[1]]
            headr.append( regnotxt.strip() )
            if regnotxt.find("/A") >= 1:
                headr.append(  line[bmw_base_orderdate[0]+1:bmw_base_orderdate[1] + 1]  )
            else:
                headr.append(  line[bmw_base_orderdate[0]:bmw_base_orderdate[1]]  )
            
            mileage = line[bmw_base_mileage[0]:bmw_base_mileage[1]].strip()
            if mileage.find("|") >= 1:
                mileage = mileage[:-1]
                headr.append(  mileage.strip() )
            else:
                headr.append(  mileage.strip() )

            orderno = line[bmw_base_orderno[0]:bmw_base_orderno[1]]
            if orderno.find("|") >= 1:
                headr.append( line[bmw_base_orderno[0]-1:bmw_base_orderno[1]-1])
            else:
                headr.append(orderno)

            invoicedate = line[bmw_base_invoicedate[0]:bmw_base_invoicedate[1]]
            if invoicedate.find("|") >=1:
                headr.append( line[bmw_base_orderdate[0]:bmw_base_orderdate[1]] )
            else:
                headr.append(invoicedate)

            SqlWrite(datatype,headr)
            pass
        if datatype=="LABOR" and dataread and line.find(conf.dealer_id) >= 1:
            labor = []
            labor.append( line[bmw_labor_dealerid[0]:bmw_labor_dealerid[1]] )
            labor.append( line[bmw_labor_invoiceid[0]:bmw_labor_invoiceid[1]] )
            labor.append( line[bmw_labor_wipno[0]:bmw_labor_wipno[1]] )
            labor.append( line[bmw_labor_itemcode[0]:bmw_labor_itemcode[1]].strip() )
            labor.append( line[bmw_labor_description[0]:bmw_labor_description[1]].strip() )
            labor.append( line[bmw_labor_qty[0]:bmw_labor_qty[1]].strip() )
            labor.append( line[bmw_labor_unit[0]:bmw_labor_unit[1]].strip() )
            labor.append( line[bmw_labor_txtdescription[0]:bmw_labor_txtdescription[1]].strip() )
            SqlWrite(datatype,labor)
            pass
        if datatype=="Parts" and dataread and line.find(conf.dealer_id) >= 1:
            parts = []
            linestr = line
            #行解析，查找 | 字符的位置并且去重和排序list
            wx = 0
            ss = [1]
            while wx <= len(line):
                wx = wx+1
                if line.find("|",wx) >= 1:
                    ss.append(line.find("|",wx))
            addr_to = list(set(ss))
            addr_to.sort(key=ss.index)
            #块范围解析
            ws = 0
            sss = []
            while ws <= len(addr_to):
                try:
                    #数据处理，将格式化的数据加入到 sss[]
                    strr = linestr[addr_to[int(ws)] : addr_to[int(ws)+1]]
                    strr = strr.strip("|").strip()
                    sss.append(strr)
                except :
                    pass
                ws = ws + 1
            CurrerLineStrSumLABOR.append(str(len(line)))   #行字符数
            SqlWrite(datatype,sss)  #输出数组
            pass

    clsl = ','.join(CurrerLineStrSumLABOR)
    log.log_append("CurrerLineStrSumLABOR: " + clsl)
    log.log_append("----------END:readfile() ------------")
    pass

#整理数据，传送到数据库
def SqlWrite(datatype,listdate):
    log.log_sql_append( "log.sql#] sqlwrite:" )
    log.log_sql_append( datatype )
    log.log_sql_append( ','.join(listdate))

    sqlconn = sql.connect('datebase.db')

    if datatype == "HEADR":
        SqlWrite_HEADR(listdate)
    elif datatype == "LABOR":
        SqlWrite_LABOR(listdate)
    elif datatype == "Parts":
        SqlWrite_Parts(listdate)

    pass
def SqlWrite_HEADR(listdate):
    #log_sql#]44144,411166,LBVHZ1100JML37210,粤QND397,2018/11/13,19134,18/11/1319409,2018/11/13
    #经销商编号，结算单编号，底盘号，车牌，工单日期，里程，日期+工单号，结算单日期
    newlistdate = [] 
    newlistdate = listdate
    newlistdate.append("0")
    newlistdate.append(str(bmw_guid))
    sqlconn = sql.connect('datebase.db')
    sqlcmd = sqlconn.cursor()
    sqlcmd.executemany("INSERT INTO " + conf.mod_parameters_sqltable[0] + " VALUES ( ?,?,?,?,?,?,?,?,?,? )",[(newlistdate)])
    sqlconn.commit()
    sqlconn.close()
    pass
def SqlWrite_LABOR(listdate):
    #log_sql#]44144,411169,19839,5214901,,9.00,5,更新左前或右前座椅座套
    #经销商编号，结算单号，工单号，工时代码，工时描述，数量，工时单位
    newlistdate = []
    newlistdate = listdate
    sqlconn = sql.connect('datebase.db')
    sqlcmd = sqlconn.cursor()
    newlistdate.append(str(bmw_guid))
    if newlistdate[4] == "":
        newlistdate[4] = " "
    sqlcmd.executemany("INSERT INTO " + conf.mod_parameters_sqltable[1] + " VALUES (?,?,?,?,?,?,?,?,?)",[(newlistdate)])
    sqlconn.commit()
    sqlconn.close()
    pass
def SqlWrite_Parts(listdate):
    #log_sql#]44144,411176,19909,,,B83.21.2.365.711,润滑油,6.5000,,,,,,,,,,,,,
    #经销商编号，结算单编号，工单号，，，零件号，零件描述，数量
    newlistdate = []
    newlistdate = listdate
    sqlconn = sql.connect('datebase.db')
    sqlcmd = sqlconn.cursor()
    sqlcmd.executemany("INSERT INTO " + conf.mod_parameters_sqltable[2] + " VALUES (?,?,?,?,?,?,?)",[(newlistdate[0],newlistdate[1],newlistdate[2],newlistdate[5],newlistdate[6],newlistdate[7],str(bmw_guid))])
    sqlconn.commit()
    sqlconn.close()
    pass


for i in bmw_datafile:
    readfile(conf.mod_parameters[0] + "/" + str(i))
    pass



