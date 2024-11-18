import os.path
import re
import threading
from shutil import copyfile

from bs4 import BeautifulSoup
import subprocess
class Student:
    def __init__(self,seq, number, name,className,submitTime,answer):
        self.seq = seq
        self.number = number
        self.name = name
        self.className = className
        self.submitTime = submitTime
        self.answer = answer
        self.workDir = None

    def setWorkDir(self, parentDir):
        self.workDir = os.path.join(parentDir, str(self.number) + self.name)
    def __str__(self) -> str:
        return  ("seq:{} \n" + \
                "number:{} \n" + \
                "name:{} \n" + \
                "className:{} \n" + \
                "submitTime:{} \n" + \
                "answer:\n{} \n").format(self.seq, self.number,self.name,self.className,self.submitTime,self.answer)
    @staticmethod
    def getStudentListFromHTML(htmlDoc:str):
        studentList = []
        studentInfoPattern = re.compile(r"(\d*) (.*) (\S*) 提交时间:(.*)")#补交没有提交时间

        soup = BeautifulSoup(htmlDoc, "html.parser")

        for i in soup.find_all("font", color="blue"):
            if (len(studentInfoPattern.findall(i.text)) == 0):
                #print(i.text)
                i.extract()

        studentInfoList = soup.find_all("font",color="blue")
        answerList = soup.find_all("code")
        answerList = answerList[len(answerList) - len(studentInfoList):]#可能案例会有多个code块
        for seq,(studentInfo,answer) in enumerate(zip(studentInfoList, answerList)):
            print(studentInfo.text)
            lis = studentInfoPattern.findall(studentInfo.text)[0]
            studentList.append(Student(seq, *lis, answer.text))
        return studentList

    def getFileName(self):
        return self.number + self.name + ".py"

    #环境准备，主要就是复制几个文件
    def envPrepare(self):
        srcDir = "studentRunEnvFiles"
        #前一个是需要链接的目录，后一个为True的话则连目录本身一起复制，如果为false则只复制目录下面的文件, 只处理一层
        # linkDirs = [("studentRunEnvFiles/aidFuncs", False), ("studentRunEnvFiles/ghostScript", True)]
        # copyDirs = [("studentRunEnvFiles/inputFiles", False)]

        # 全改复制能避免硬链接超出的问题, ghostScript改了下搜索方法不再需要复制了
        linkDirs = []
        copyDirs = [("studentRunEnvFiles/aidFuncs", False), ("studentRunEnvFiles/inputFiles", False)]

        if not os.path.isdir(self.workDir):
            os.mkdir(self.workDir)

        for linkDir, dirCopyFlag in linkDirs:
            fileList = [fileName for fileName in os.listdir(linkDir) if os.path.isfile(os.path.join(linkDir, fileName))]
            desDir = self.workDir
            if dirCopyFlag:
                desDir = os.path.join(self.workDir,os.path.basename(linkDir))
                if not os.path.exists(desDir):
                    os.mkdir(desDir)
            for fileName in fileList:
                desPath = os.path.abspath(os.path.join(desDir, fileName))
                srcPath = os.path.abspath(os.path.join(linkDir, fileName))
                if not os.path.exists(desPath):
                    #软链接的适配性好一点
                    #os.symlink(srcPath,desPath)
                    #但软链接要权限，忘记管理员启动还要重新打开，还是用硬链接算了
                    os.link(srcPath, desPath)


        for copyDir, dirCopyFlag in copyDirs:
            fileList = [fileName for fileName in os.listdir(copyDir) if os.path.isfile(os.path.join(copyDir, fileName))]
            desDir = self.workDir
            if dirCopyFlag:
                desDir = os.path.join(self.workDir, os.path.basename(copyDir))
                if not os.path.exists(desDir):
                    os.mkdir(desDir)
            for fileName in fileList:
                desPath = os.path.abspath(os.path.join(desDir, fileName))
                srcPath = os.path.abspath(os.path.join(copyDir, fileName))
                if not os.path.exists(desPath):
                    copyfile(srcPath, desPath)

    # 答案预处理, 插入几个import语句
    def answerPreprocessing(self):
        # 处理换行问题，直接插入hook后的所有函数
        hookInputStr = "from hookFunctions import *\n"

        # 处理下汇率转化问题的货币符号问题
        # self.answer = self.answer.replace("＄", "$")
        # self.answer = self.answer.replace("¥", "￥")
        answer2 = hookInputStr + self.answer

        # 处理画图的问题，在main函数后截获数据并编码为base64传输到前端
        answer2 += "\n" + "import afterMainProcess"
        self.answer = answer2

    def runFilePrepare(self,inputStr):
        pyFile = os.path.join(self.workDir, self.getFileName())
        with open(pyFile, "w", encoding="utf-8") as f:
            f.write(self.answer)
        inputFile = os.path.join(self.workDir, self.getFileName() + ".input.txt")
        with open(inputFile, "w", encoding="utf-8") as f:
            f.write(inputStr)
        return pyFile, inputFile

    def testAnswer(self, inputStr):
        self.envPrepare()
        self.answerPreprocessing()
        pyFile, inputFile = self.runFilePrepare(inputStr)
        cmd = "python -u {} < {} 2>&1".format(pyFile, inputFile)
        with os.popen(cmd) as popen:
            out = popen.buffer.read().decode("utf-8")
        #print(str(self.seq) + self.name)
        out = out.replace("\r\n", "\n")
        if "<img src=\"data:image/jpg;base64" not in out:
            out = out.replace("<", "&lt;")
            out = out.replace(">", "&gt;")
        #out += "\n \\n number:{}".format(out.count("\n"))
        return out
    @staticmethod
    def testFile(pyFile, inputFile):
        cmd = "python -u {} < {} 2>&1".format(pyFile, inputFile)
        with os.popen(cmd) as popen:
            out = popen.buffer.read().decode("utf-8")
        # print(str(self.seq) + self.name)
        out = out.replace("\r\n", "\n")

        return out
