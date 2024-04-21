#在main结束之后处理一些东西
#目前主要是处理
#1. turtle画的图片的返回值,用base64编码返回
import base64
import io
import os
import re
import sys
import tempfile
import threading
from pythonOJConfig import *
from hookFunctions import pythonOjOldOpen
from hookFunctions import endRunLimitTimer
endRunLimitTimer()
import uuid
moduleAndExitFunction = {}



def atTurtleExit():
    import turtle
    turtle.update()
    # 生成一个随机字符串
    tempFile = sys.argv[0] + ".turtle.eps"
    turtle.getscreen().getcanvas().postscript(file=tempFile)
    from PIL import Image, EpsImagePlugin
    EpsImagePlugin.gs_windows_binary = r'./ghostScript/gswin64c.exe'

    img = Image.open(tempFile)
    img = img.resize((300,300))
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    byte_data = img_buffer.getvalue()

    img_buffer.close()
    img.close()
    os.remove(tempFile)

    base64_str = base64.b64encode(byte_data).decode('utf-8')
    print("<img src=\"{}\"/>".format("data:image/jpg;base64," + base64_str))

moduleAndExitFunction["turtle"] = atTurtleExit

for moduleName, exitFunction in moduleAndExitFunction.items():
    if hasModule(moduleName):
        exitFunction()

for fo in pythonOJOpenFoList:
    fo.close()

for fileName in pythonOJNeedReadFileList:
    print("\n","-"*10, fileName, '-'*10)
    fo = pythonOjOldOpen(fileName, "r", encoding="utf-8")
    print(fo.read(), end="")




# def f_read(filename,split_char):
#     f=open(filename,"r")
#     s=f.read()  #读入全部内容
#     a=s.split("\n")
#     max=''    #表示还没有最大值
#     for i in a:
#         b=i.split(split_char)
#         for j in b:
#             if j=="" or j=="\n":
#                 continue
#             if max=='':
#                 max = eval(j)
#             elif j != '':
#                 if eval(j)>max:
#                     max=eval(j)
#     f.close()
#     print("正确答案:用read求全部数字的最大值:{}".format(max))
#
#
# #用readlines求每行数字和的最大值
# def f_readlines(filename,split_char):
#     f=open(filename,"r")
#     max=''
#     for line in f.readlines():  #这句也可以改成 for line in f:
#         b=line.split(split_char)
#         sum=0
#         for j in b:
#             if j == "" or j == "\n":
#                 continue
#             sum = sum + eval(j)
#
#         if max=='':
#             max = sum
#         elif sum>max:
#             max = sum
#     f.close()
#     print("正确答案:用readlines求每行和的最大值:{}".format(max))
#适用于随机数生成文件的题目，用来检测答案的正确性,看题目随时更改
# def check_answer():
#     filename = "./data.txt"
#     f = open(filename, "r")
#     content = f.read()  # 读入全部内容
#     for i in range(10):
#         content = content.replace(str(i),"")
#     content = content.replace("-", "")
#     content = set(content)
#     content.remove("\n")
#     split_char= list(content)[0]
#     print("split_char:'{}'".format(split_char))
#     f.close()
#     f_read(filename,split_char)
#     f_readlines(filename,split_char)
# check_answer()

#检测某些函数是否被调用
# def check_func():
#     ban_func = ["max", "sort", "sorted"]
#     for funcName in ban_func:
#         pattern = re.compile(r"{}[(].*?[)]".format(funcName))
#         if pattern.search(fileContent) != None:
#             print("{}函数被调用".format(funcName))
# check_func()




