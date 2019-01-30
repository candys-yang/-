# -*- coding: UTF-8 -*-


'''

    该文件定义了 汽车健康档案 大部分的功能。
    配置项遵循 python 语法标准。

    日期：2019-1-30   作者：杨主任
    Email： 522703331@qq.com 
    GIT：https://github.com/candys-yang/
    blog：http://varmain.com

'''


import os,uuid

#         基本配置信息
#   这部分定义了软件的基础项目
#   注意：这里的每一个配置项都是有意义的。



# 软件主目录，默认将获取当前所在目录
python_dir = os.getcwd()


# ------------- 经销商信息 ---------------
# 经销商名称
dealer_name = "某某某宝汽车销售服务有限公司"
# 经销商编码
dealer_id = "00000"
#汽车品牌，示例：BMW     LEXUS       Toyota      Honda
dealer_brand = "BMW"



# ------------- 网管数据 ----------------
# 显式调式数据
itadmin_debug = True
# 启用日志
itadmin_log = True                      # Default As True



# 账号数据
itadmin_update_url = "https://abc.com/update"      #上传地址
itadmin_update_token = "https://abc.com/token"  #token验证地址
itadmin_update_user = "username"                #上传登陆用户名
itadmin_update_pwd = "password"                 #上传登陆密码


# ---------------- 模块系统 ----------------
# 指定数据处理模块：
#   数据处理模块的实例文件位于 script 目录下
mod_script = "5990"
#   定义模块所需的参数，格式为标准的：python list 
#   mod_parameters[0] = DMS的数据目录
#   mod_parameters[1] = 表映射
mod_parameters_sqltable = ["bmw_headr","bmw_labor","bmw_parts"]
mod_parameters = ['D:/upload',mod_parameters_sqltable]




