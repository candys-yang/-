# -*- coding: UTF-8 -*-


'''

    这是软件的主入口
    当该文件运行时，将会根据 conf.py 文件进行一系列的数据处理。

    日期：2018-12-12   作者：杨主任
    Email： 522703331@qq.com 
    GIT：https://github.com/candys-yang/
    blog：http://varmain.com

'''




#标准库
import os
import sys
#第三方库


#本地库
import conf


# ------------ 预初始化指令 ------------
# 模块搜索
sys.path.append(conf.python_dir + "/script")
print(conf.python_dir)
__import__( conf.dealer_brand )     #加载品牌数据处理模块
__import__( conf.mod_script )       #加载城市编码数据处理模块
#exit()



