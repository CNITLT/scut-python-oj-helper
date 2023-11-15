import os
import sys
import re
from shutil import copyfile

import pandas

from pythonOJConfig import *
import threading
import time
import pandas as pd
pythonOJOldInput = input

moduleAndHookFunction = {}
def input(*args, **kwargs):
    res = pythonOJOldInput(*args, **kwargs)
    print(res)
    return res

def turtleHook():
    import turtle
    # 关闭会话过程
    turtle.tracer(False)
    # 屏蔽done,防止卡死
    turtle.done = lambda *args, **kwargs: None
    # 规定画布大写，这个依据题目频繁的改
    turtle.setup(800, 800, None, None)
    turtle.setup = lambda *args, **kwargs: None
    turtle._Screen.exitonclick = lambda *args, **kwargs: None
    turtle._Screen.mainloop = lambda *args, **kwargs: None
    turtle.mainloop = lambda *args, **kwargs: None
moduleAndHookFunction["turtle"] = turtleHook


pythonOJOldRandomSeed = None
def fixRandomSeed():
    """
    固定随机数，保证生成的随机数序列是固定的，方便判断
    """
    import random
    random.seed(2023)
    pythonOJOldRandomSeed = random.seed
    random.seed = lambda *args, **kwargs: None

moduleAndHookFunction["random"] = fixRandomSeed

pythonOjOldOpen = open
open = open
def pythonOjOpen(*args,**kwargs):
    #看情况需要固定一个输入的文件名，根据题目判断是否需要注释
    # if (len(args) >= 2 and ("r" in args[1] or "+" in args[1])):
    #     args = list(args)
    #     args[0] = "2015年5月高三模拟考成绩.csv"
    #     args = tuple(args)
    #     kwargs["encoding"] = "utf8"
    if fixOpenedFileNameFlag:
        return pythonOjOldOpen(openedFileName, "r",encoding="utf-8")
    # 只能打开工作目录下的文件,打开别的地方的直接关掉程序
    workDir = os.path.abspath(os.getcwd())
    absFilePath = os.path.abspath(args[0])

    if not absFilePath.startswith(workDir):
        print(sys.argv[0], "正在打开非工作目录下的文件")
        exit(-1)

    if args[0] not in pythonOJNeedReadFileList:
        pythonOJNeedReadFileList.append(args[0])
    fo = pythonOjOldOpen(*args,**kwargs)
    pythonOJOpenFoList.append(fo)
    return fo


def hookOpen():
    global open
    open = pythonOjOpen
hookOpen()





def pandasHook():
    import pandas
    oldRead_csv = pandas.read_csv
    oldRead_excel = pandas.read_excel
    def pythonOjPandasRead_csv(*args, **kwargs):
        if fixOpenedFileNameFlag:
            args = list(args)
            args[0] = openedFileName
            args = tuple(args)
            return oldRead_csv(*args, **kwargs)
        # 只能打开工作目录下的文件,打开别的地方的直接关掉程序
        workDir = os.path.abspath(os.getcwd())
        absFilePath = os.path.abspath(args[0])

        if not absFilePath.startswith(workDir):
            print(sys.argv[0], "正在打开非工作目录下的文件")
            exit(-1)

        if args[0] not in pythonOJNeedReadFileList:
            pythonOJNeedReadFileList.append(args[0])
        fo = oldRead_csv(*args, **kwargs)
        pythonOJOpenFoList.append(fo)
        return fo
    pandas.read_csv = pythonOjPandasRead_csv
    def pythonOjPandasRead_excel(*args, **kwargs):
        if fixOpenedFileNameFlag:
            args = list(args)
            args[0] = openedFileName
            args = tuple(args)
            return oldRead_excel(*args, **kwargs)
        # 只能打开工作目录下的文件,打开别的地方的直接关掉程序
        workDir = os.path.abspath(os.getcwd())
        absFilePath = os.path.abspath(args[0])

        if not absFilePath.startswith(workDir):
            print(sys.argv[0], "正在打开非工作目录下的文件")
            exit(-1)

        if args[0] not in pythonOJNeedReadFileList:
            pythonOJNeedReadFileList.append(args[0])
        fo = oldRead_excel(*args, **kwargs)
        pythonOJOpenFoList.append(fo)
        return fo
    pandas.read_excel = pythonOjPandasRead_excel


moduleAndHookFunction["pandas"] = pandasHook

for moduleName,hookFunction in moduleAndHookFunction.items():
    if hasModule(moduleName):
        hookFunction()


timerEnd = False
def startRunLimitTimer():
    """
    开启一个定时器，如果程序内有死循环的程序超时就自动退出
    """

    def timerLimitExit():
        if pythonOJRunTimeLimit <= 0:
            return
        time.sleep(pythonOJRunTimeLimit)
        if timerEnd:
            return
        print("Timeout Error:run more than {}s without exiting".format(pythonOJRunTimeLimit))
        os._exit(-int(pythonOJRunTimeLimit))

    timer = threading.Thread(target=timerLimitExit, daemon=True)
    if DebugModeFlag == False:
        timer.start()

def endRunLimitTimer():
    timerEnd = True


startRunLimitTimer()
