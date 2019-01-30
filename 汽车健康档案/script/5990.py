#coding=utf-8

import os,sqlite3,json,requests
import log,conf


log.log_append("Load 5990.py")

'''

    该模块将负责处理数据并整理上传到服务器

    日期：2019-1-30   作者：杨主任
    Email： 522703331@qq.com 
    GIT：https://github.com/candys-yang/
    blog：http://varmain.com

'''


#-------------公共变量区域------------
databaselist = []   #从数据库中解析主记录循环
tokenstr = ["",""]  #token地址



#-------------- 宝马品牌私有函数 ----------------
#bmw数据json化
def bmw_jsonstr_main():
    ''' bmw数据json化处理'''
    bmw_jsonstr_databaselist()
    #每条主记录循环一次
    for x in databaselist:
        bjpar = [] 
        bjpar = bmw_jsonstr_partxt(x)
        bjhor = []
        bjhor = bmw_jsonstr_hor(x)

		#整理数据json字符 ↓
        tttre = '{ "access_token":"' + str(tokenstr[0]) + '","basicInfo":{'
        if x[3] == "N/A":
            tttre = tttre + '"vehicleplatenumber":"' + '",'
        else:
            tttre = tttre + '"vehicleplatenumber":"' + x[3] + '",'
        tttre = tttre + '"companyname":"' + conf.dealer_name + '",'
        tttre = tttre + '"vin":"' + x[2] + '",'
        tttre = tttre + '"repairdate":"' + str(x[4]).replace('/','') + '",'    #"repairdate":"20181113",
        tttre = tttre + '"repairmileage":"' + str(x[5]) + '",'    #"repairmileage":"19134",
        tttre = tttre + '"settledate":"' + str(x[7]).replace('/','') + '",'      # "settledate":"20181212",
        tttre = tttre + '"faultdescription":"'+ bmw_jsonstr_hor_faultdescription(x) + '",'    #"faultdescription":"无",
        tttre = tttre + '"costlistcode":"' + str(x[4]).replace('/','') + x[1] + '"},'    #"costlistcode":"20181113411166"},
        tttre = tttre + '"vehiclepartslist":[ '
        for x in bjpar:
            tttre = tttre + '{"partscode":"' + x[3] + '",'      
            tttre = tttre + '"partsquantity":"' + str(x[5]) + '",'    
            tttre = tttre + '"partsname":"' + x[4] + '"},'    
            pass
        tttre = tttre[:-1]
        tttre = tttre + "],"
        tttre = tttre + '"repairprojectlist":['
        for y in bjhor:
            tttre = tttre + '{"repairproject":"' + y[7] +'","workinghours":"' + str(y[5]) + '"},' 
            pass
        if len(bjhor) >= 1:
            tttre = tttre[:-1]
            pass
        tttre = tttre + "]}"
        log.log_append( "all json str = " + str(tttre))
        #提交 json 数据到服务器
        postdata(tttre)

        pass
    pass


def bmw_jsonstr_databaselist():
    '''
    从数据库获取数据并list化
    返回所有 bmw_headr.upstart = 0 的行
    返回的结果存放在 databaselist[] 中。
    '''
    sqlconn = sqlite3.connect('datebase.db')
    sqlcmd = sqlconn.cursor()

    sqllist = sqlcmd.execute("select * from bmw_headr where upstart = 0 and regno <> '无'")
    for x in sqllist:
        databaselist.append(x)
        pass
    log.log_append("get database bmw_headr data :" + str(databaselist))

    sqlconn.close()
    pass

def bmw_jsonstr_partxt(invid):
	'''提取记录配件信息'''
	sqlconn = sqlite3.connect('datebase.db')
	sqlcmd = sqlconn.cursor()
	sqlread = sqlcmd.execute("select * from bmw_parts where invoiceid = ?",[str(invid[1])])
	re = []
	for x in sqlread:
		re.append(x)
		pass
	log.log_append("get bmw_parts :" + str(re))
	return re
	pass

def bmw_jsonstr_hor(invid):
	''' 获取工时信息记录 ，返回数据库记录的数组 '''
	sqlconn = sqlite3.connect('datebase.db')
	sqlcmd = sqlconn.cursor()
	sqlread = sqlcmd.execute("select * from bmw_labor where invoiceid = ?",[str(invid[1])])
	re = []
	for x in sqlread:
		re.append(x)
		pass
	log.log_append("get bmw_labor :" + str(re))
	sqlconn.close()
	return re
	pass

#提取故障描述信息
def bmw_jsonstr_hor_faultdescription(invid):
    sqlconn = sqlite3.connect('datebase.db')
    sqlcmd = sqlconn.cursor()
    sqlread = sqlcmd.execute("select * from bmw_labor where invoiceid = ? and itemcode = 'TXT'",[(invid[1])])
    re = []
    for x in sqlread:
        re.append(x)
        pass
    sqlconn.close()
    res = "无"
    try:
        res = re[0][7]
    except:
        log.log_append("5990.py bmw_jsonstr_hor_faultdescription() try ，不是有效的记录，返回“无”：" + str(sqlread))
    return res
    pass
#---------------------------------------------------


def gettoken():
    '''获取token的值，改写变量：tokenstr[状态码，token值]'''
    url = conf.itadmin_update_token
    js = {"companycode":str(conf.itadmin_update_user),"companypassword":str(conf.itadmin_update_pwd)}
    headers = {'content-type': "application/json"}
    response = requests.post(url, data = json.dumps(js), headers = headers , verify=False)
    getstr = response.text
    text = json.loads(getstr)
    if str(text['code']) == "1":
        tokenstr[0] = text['access_token']
        log.log_append("get token val: " + tokenstr[0])
    else:
        tokenstr[0] = "0"
        tokenstr[1] = getstr
        log.log_append("get token fail!!!")
    pass

def postdata(jsonstr):
    '''
    提交健康档案信息，并更新数据库记录。
    改写 bmw_headr.upstart 
    '''
    url = conf.itadmin_update_url
    js = jsonstr.encode('utf-8')
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data = js ,headers = headers , verify=False )
    getstr = response.text
    #getstr = '{ "code":"1" }'
    text = json.loads(getstr)
    if text['code'] == "1":
        #重新提取结算单号           jsonarr['basicInfo']['costlistcode']
        jsonarr = json.loads(jsonstr)
        biclc = jsonarr['basicInfo']['costlistcode']
        biclc =biclc[8:]
        sqlconn = sqlite3.connect('datebase.db')
        sqlcmd = sqlconn.cursor()
        sqlread = sqlcmd.execute("update [bmw_headr] set upstart = 1 where invocieid = ?",[biclc])
        sqlconn.commit()
        log.log_append("post success , database update [bmw_headr.upstart] = 1 for :" + str(biclc))
    else:
        sqlconn = sqlite3.connect('datebase.db')
        sqlcmd = sqlconn.cursor()
        sqlread = sqlcmd.execute("update [bmw_headr] set upstart = 2 where invocieid = ?",[biclc])
        sqlconn.commit()
        log.log_append("post fail , database update [bmw_headr.upstart] = 2 for :" + str(biclc) + "----> " + getstr)
    pass



#分析品牌，实施任务
if conf.dealer_brand == "BMW":
    gettoken()
    if tokenstr[0] == "0":
        log.log_append("token fail! "  + str(tokenstr[1]))
    else:
		#实施json上传的主进程。
        bmw_jsonstr_main()

