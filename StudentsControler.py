import datetime
import time
from multiprocessing import cpu_count

from Student import Student
from Question import Question
import os
from concurrent.futures import ThreadPoolExecutor
from studentRunEnvFiles.aidFuncs.pythonOJConfig import maxWorkThreadNum
def testAnswer(student,inputStr):
    print(student.seq, " ", student.name)
    res = student.testAnswer(inputStr)
    return {student.seq:res}

class StudentsControler:
    cache = {}
    BaseDir = "codes"
    def __init__(self, htmlDoc, inputStr):
        self.question = Question.getQuestion(htmlDoc)
        self.studentList = Student.getStudentListFromHTML(htmlDoc)
        self.inputStr =inputStr
    #前期环境准备，主要就是几个文件夹创建
    def preprocess(self):
        nowProcessDir = StudentsControler.BaseDir
        if not os.path.isdir(nowProcessDir):
            os.mkdir(nowProcessDir)
        # 根据当前时间创建一个目录, 用来存当前问题的运行代码, 不考虑冲突问题
        timeStr = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
        nowProcessDir = os.path.join(nowProcessDir, timeStr)
        os.mkdir(nowProcessDir)
        with open(os.path.join(nowProcessDir, "Question.txt"), "w", encoding="utf-8") as f:
            f.write(self.question)
        for student in self.studentList:
            student.setWorkDir(nowProcessDir)

    def run(self):
        # 加一层缓存
        hash_doc = hash(self.question)
        hash_input = hash(self.inputStr) + len(self.studentList)  # 只显示需要批改作业会导致数量变化，这点要考虑到
        print("hash_doc:{} hash_input:{}".format(hash_doc, hash_input))
        if hash_doc in StudentsControler.cache:
            if hash_input in StudentsControler.cache[hash_doc]:
                print("cache hit [{}][{}]".format(hash_doc, hash_input))
                return StudentsControler.cache[hash_doc][hash_input]
        self.preprocess()

        res = {}
        with ThreadPoolExecutor(max_workers=min(maxWorkThreadNum,cpu_count())) as threadPool:
            for ret in threadPool.map(testAnswer, self.studentList, [self.inputStr] * len(self.studentList)):
                # print(list(ret.keys())[0])
                res.update(ret)
        print(res)

        # 加入缓存
        if hash_doc not in StudentsControler.cache:
            StudentsControler.cache[hash_doc] = {}
        print("cache store [{}][{}]".format(hash_doc, hash_input))
        StudentsControler.cache[hash_doc][hash_input] = res
        return res



