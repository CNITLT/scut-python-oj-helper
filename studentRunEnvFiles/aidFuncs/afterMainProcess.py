#在main结束之后处理一些东西
#目前主要是处理
#1. turtle画的图片的返回值,用base64编码返回
import base64
import io
import os
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
