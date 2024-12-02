import os
import random
import sys
import re
from shutil import copyfile
import weakref
import pandas

from pythonOJConfig import *
import threading
import time
import pandas as pd
pythonOJOldInput = input

moduleAndHookFunction = {}
pythonOJInputUsedFlag = False
def input(*args, **kwargs):
    global pythonOJInputUsedFlag
    pythonOJInputUsedFlag = True
    try:
        res = pythonOJOldInput(*args, **kwargs)
    except Exception as e:
        print(e)
        os._exit(-1) #防止把try 放到while True里给弄成死循环
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
pythonOJOldRandInt = random.randint
def fixRandomSeed():
    """
    固定随机数，保证生成的随机数序列是固定的，方便判断
    """
    import random
    random.seed(1000)
    pythonOJOldRandomSeed = random.seed
    random.seed = lambda *args, **kwargs: None
    random.randint = lambda a,b: int(random.random() * (b-a+1) + a)
    random.randrange = lambda a,b,*args,**kwargs: int(random.random() * (b-a+1) + a)
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
    # if "r" not in args[1]:
    #     workDir = os.path.abspath(os.getcwd())
    #     absFilePath = os.path.abspath(args[0])
    #
    #     if not absFilePath.startswith(workDir):
    #         print(sys.argv[0], "正在打开非工作目录下的文件")
    #         exit(-1)
    #     return pythonOjOldOpen(openedFileName, args[1],encoding="utf-8")

    if fixOpenedFileNameFlag:
        args = list(args)
        args[0] = openedFileName
        args = tuple(args)
        if "encoding" not in kwargs:
            kwargs["encoding"] = "utf-8"
        return pythonOjOldOpen(*args,**kwargs)

    #打开的文件目录全部切换到工作目录下
    filename = os.path.basename(args[0])
    args = list(args)
    args[0] = "./{}".format(filename)
    args = tuple(args)

    # 只能打开工作目录下的文件,打开别的地方的直接关掉程序
    workDir = os.path.abspath(os.getcwd())
    absFilePath = os.path.abspath(args[0])

    if not absFilePath.startswith(workDir):
        print(sys.argv[0], "正在打开非工作目录下的文件")
        exit(-1)

    if args[0] not in pythonOJNeedReadFileList:
        pythonOJNeedReadFileList.append(args[0])
    fo = pythonOjOldOpen(*args,**kwargs)
    pythonOJOpenFoList.append(weakref.ref(fo))
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
    global timerEnd
    timerEnd = True


startRunLimitTimer()

s = '''双儿 洪七公 赵敏 赵敏 逍遥子 鳌拜 殷天正 金轮法王 乔峰 杨过 洪七公 郭靖 
       杨逍 鳌拜 殷天正 段誉 杨逍 慕容复 阿紫 慕容复 郭芙 乔峰 令狐冲 郭芙 
       金轮法王 小龙女 杨过 慕容复 梅超风 李莫愁 洪七公 张无忌 梅超风 杨逍 
       鳌拜 岳不群 黄药师 黄蓉 段誉 金轮法王 忽必烈 忽必烈 张三丰 乔峰 乔峰 
       阿紫 乔峰 金轮法王 袁冠南 张无忌 郭襄 黄蓉 李莫愁 赵敏 赵敏 郭芙 张三丰 
       乔峰 赵敏 梅超风 双儿 鳌拜 陈家洛 袁冠南 郭芙 郭芙 杨逍 赵敏 金轮法王 
       忽必烈 慕容复 张三丰 赵敏 杨逍 令狐冲 黄药师 袁冠南 杨逍 完颜洪烈 殷天正 
       李莫愁 阿紫 逍遥子 乔峰 逍遥子 完颜洪烈 郭芙 杨逍 张无忌 杨过 慕容复 
       逍遥子 虚竹 双儿 乔峰 郭芙 黄蓉 李莫愁 陈家洛 杨过 忽必烈 鳌拜 王语嫣 
       洪七公 韦小宝 阿朱 梅超风 段誉 岳灵珊 完颜洪烈 乔峰 段誉 杨过 杨过 慕容复 
       黄蓉 杨过 阿紫 杨逍 张三丰 张三丰 赵敏 张三丰 杨逍 黄蓉 金轮法王 郭襄 
       张三丰 令狐冲 赵敏 郭芙 韦小宝 黄药师 阿紫 韦小宝 金轮法王 杨逍 令狐冲 阿紫 
       洪七公 袁冠南 双儿 郭靖 鳌拜 谢逊 阿紫 郭襄 梅超风 张无忌 段誉 忽必烈 
       完颜洪烈 双儿 逍遥子 谢逊 完颜洪烈 殷天正 金轮法王 张三丰 双儿 郭襄 阿朱 
       郭襄 双儿 李莫愁 郭襄 忽必烈 金轮法王 张无忌 鳌拜 忽必烈 郭襄 令狐冲 
       谢逊 梅超风 殷天正 段誉 袁冠南 张三丰 王语嫣 阿紫 谢逊 杨过 郭靖 黄蓉 
       双儿 灭绝师太 段誉 张无忌 陈家洛 黄蓉 鳌拜 黄药师 逍遥子 忽必烈 赵敏 
       逍遥子 完颜洪烈 金轮法王 双儿 鳌拜 洪七公 郭芙 郭襄 赵敏'''

# 记录下当前服务端定义的函数，等会用于排查出学生的函数
pythonOJFuncDict = {}
for key,value in list(globals().items()):
    if callable(value):
        pythonOJFuncDict[key] = value
