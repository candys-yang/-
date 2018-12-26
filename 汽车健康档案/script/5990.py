#coding=utf-8

import os,sqlite3,json,requests
import log,conf


log.log_append("Load 5990.py")

'''

    该模块将负责处理数据并整理上传到服务器

    日期：2018-12-12   作者：杨主任
    Email： 522703331@qq.com 
    GIT：https://github.com/candys-yang/
    blog：http://varmain.com

'''

'''
---------------健康档案系统的 API ----------------------
#身份验证
{
"companycode":"维修企业编码",
"companypassword":"密码"，
}
#回调参数：
{
"code":"1",
"status":"获取成功",
"accsss_token":"32位票据",
}
或
{
"code": "-1", "status": "参数无效",
"code": "-2", "status":"参数格式不对",
"code": "-10", "status": "企业不存在"
"code": "-11", "status": "密码错误"
"code": "-99", "status":"异常",
}
#新增维修记录：
{
    "access_token":null,
    "basicInfo":{
        "vehicleplatenumber":"粤QND397",
        "companyname":"阳江美宝行汽车销售服务有限公司",
        "vin":"LBVHZ1100JML37210",
        "repairdate":"20181113",
        "repairmileage":"19134",
        "settledate":"20181212",
        "faultdescription":"无",
        "costlistcode":"20181113411166"},
    "vehiclepartslist":[{
            "partsname":"组件.机油滤清器滤芯",
            "partsquantity":"1.00",
            "partscode":"B11.42.8.570.590"}],
    "repairprojectlist":[{
            "repairproject":"VHC车辆健康检查",
            "workinghours":"4.0"},{
            "repairproject":"悦享保养套餐—机油机滤保养费用预计：销售套餐3年6次，第2次",
            "workinghours":"0.0"},{
            "repairproject":"保养标准范围",
            "workinghours":"2.0"},{
            "repairproject":"发动机油保养",
            "workinghours":"3.0"},{
            "repairproject":"润滑油4.25L",
            "workinghours":"8.9"
    }]
}
'''
'''
--------------- 本模块的 API ----------------------
    本模块在被引用后，会调用 conf.py 的一个或多个参数。
    模块在被初始化时，会查询 conf.mod_parameters 的值，关于该参数的值，本模块的解析方式如下：
    mod_parameters = ["存放kprint导出的数据目录路径",[数据库表名],[数据列表]]   
    数据列表是本模块所调用的值，以下是该 list 对应的值
        list[1]     -->     companycode         企业编码
        list[2]     -->     companypassword     密码
        list[3]     -->     basicinfo[]
            basicinfo[0]     -->     vehicleplatenumber  车牌
            basicinfo[1]     -->     companyname
            basicinfo[2]     -->     vin
            basicinfo[3]     -->     repairdate
            basicinfo[4]     -->     repairmileage
            basicinfo[5]     -->     settledate
            basicinfo[6]     -->     faultdescription
            basicinfo[7]     -->     costlistcode
        list[4]     -->     vehiclepartslist[]
            vehiclepartslist[x]  --> vehiclepartslist_list[]
                vehiclepartslist_list[0]    -->     partscode   
                vehiclepartslist_list[1]    -->     partsquantity
                vehiclepartslist_list[2]    -->     partsname
            vehiclepartslist[x]  --> vehiclepartslist_list[]
                vehiclepartslist_list[0]    -->     partscode   
                vehiclepartslist_list[1]    -->     partsquantity
                vehiclepartslist_list[2]    -->     partsname
        list[5]     -->     repairprojectlist[]
                repairprojectlist_list[0]   -->     repairproject
                repairprojectlist_list[1]   -->     workinghours

'''

#-------------公共变量区域------------
databaselist = []   #从数据库中解析主记录循环
tokenstr = ["",""]  #token地址



#-------------- 宝马品牌私有函数 ----------------
#bmw数据json化
def bmw_jsonstr_main():
    bmw_jsonstr_databaselist()
    #每条主记录循环一次
    for x in databaselist:
        bjpar = [] 
        bjpar = bmw_jsonstr_partxt(x)
        bjhor = []
        bjhor = bmw_jsonstr_hor(x)

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
            tttre = tttre + '{"repairproject":"' + y[7] +'","workinghours":"' + str(y[5]) + '"},'      #{"repairproject":"VHC车辆健康检查","workinghours":"4.0"},
            pass
        tttre = tttre[:-1]
        tttre = tttre + "]}"
        postdata(tttre)
        pass
    pass

#从数据库获取数据并list化
def bmw_jsonstr_databaselist():
    sqlconn = sqlite3.connect('datebase.db')
    sqlcmd = sqlconn.cursor()

    sqllist = sqlcmd.execute("select * from bmw_headr where upstart = 0")
    for x in sqllist:
        databaselist.append(x)
        pass
    #print(databaselist)
    sqlconn.close()
    pass
#提取记录配件信息
def bmw_jsonstr_partxt(invid):
    #print(invid[1])
    sqlconn = sqlite3.connect('datebase.db')
    sqlcmd = sqlconn.cursor()
    sqlread = sqlcmd.execute("select * from bmw_parts where invoiceid = ?",[str(invid[1])])
    re = []
    for x in sqlread:
        re.append(x)
        pass
    return re
    pass
#提取记录工时信息
def bmw_jsonstr_hor(invid):
    #print(invid[1])
    sqlconn = sqlite3.connect('datebase.db')
    sqlcmd = sqlconn.cursor()
    sqlread = sqlcmd.execute("select * from bmw_labor where invoiceid = ?",[str(invid[1])])
    re = []
    for x in sqlread:
        re.append(x)
        pass
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
        pass
    return res
    pass
#---------------------------------------------------


#post获取 token
def gettoken():
    url = conf.itadmin_update_token
    js = {"companycode":str(conf.itadmin_update_user),"companypassword":str(conf.itadmin_update_pwd)}
    headers = {'content-type': "application/json"}
    response = requests.post(url, data = json.dumps(js), headers = headers , verify=False)
    getstr = response.text
    text = json.loads(getstr)

    if str(text['code']) == "1":
        tokenstr[0] = text['access_token']
        
    else:
        tokenstr[0] = "0"
        tokenstr[1] = getstr
    pass
#提交健康档案信息
def postdata(jsonstr):

    url = conf.itadmin_update_url
    js = jsonstr.encode('utf-8')
    headers = {'content-type': 'application/json','User-Agent':'YK-Soft 2018'}
    response = requests.post(url, data = js ,headers = headers , verify=False )
    getstr = response.text
    text = json.loads(getstr)
    log.log_append(json.loads(js))
    log.log_append(text)

    pass
#


#分析品牌，实施任务
if conf.dealer_brand == "BMW":
    gettoken()
    if tokenstr[0] == "0":
        log.log_append("token fail! "  + str(tokenstr[1]))
    else:
        bmw_jsonstr_main()
