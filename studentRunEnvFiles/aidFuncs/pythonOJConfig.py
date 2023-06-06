import os
import re
import sys

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.argv[0] = os.path.basename(sys.argv[0])

pythonOJNeedReadFileList = []
pythonOJOpenFoList = []#打开的文件流对象，有可能没关掉需要先手动关掉
DebugModeFlag = True if sys.gettrace() else False
pythonOJRunTimeLimit = 60 #单位:秒, 给小于等于0的都表示不限制运行时间


fixOpenedFileNameFlag = True
openedFileName = "整数.txt"

with open(sys.argv[0], "r", encoding="utf-8") as f:
    fileContent = f.read()

def hasModule(moduleName):
    modulePattern = re.compile("(from|import) {}".format(moduleName))
    return modulePattern.search(fileContent) != None
