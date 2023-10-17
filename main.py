import os
from concurrent.futures import ThreadPoolExecutor
import datetime
from typing import Union

import pandas as pd
from bs4 import BeautifulSoup
from pydantic import BaseModel

from Question import Question
from Student import Student

from starlette.responses import FileResponse

from fastapi import FastAPI

from multiprocessing import cpu_count

import uvicorn

from StudentsControler import StudentsControler

app = FastAPI()

def generate_all_df(htmlDoc):
    """
    生成包含所有学生信息的dataframe
    :param htmlDoc: 前端原始html字符串
    :return:包含所有学生信息的dataframe
    """
    soup = BeautifulSoup(htmlDoc, "html.parser")
    table = soup.find_all("table")
    lines = table[0].find_all("tr")
    columns = []
    for column in lines[0]:
        columns.append(column.text)
    datas = []
    for line in lines[1:]:
        data = []
        for item in line:
            item_str = item.text
            if item_str != "":
                data.append(item_str.strip())
            else:
                data.append(0)
        datas.append(data)
    all_df = pd.DataFrame(datas, columns=columns)
    if '成绩' in all_df.columns:
        all_df["成绩"] = all_df["成绩"].apply(pd.to_numeric)
    elif "平均分" in all_df.columns:
        all_df["平均分"] = all_df["平均分"].apply(pd.to_numeric)
    return all_df


def testAnswer(student,inputStr):
    print(student.seq, " ", student.name)
    res = student.testAnswer(inputStr)
    return {student.seq:res}

@app.post("/oj")
def test(doc: dict):
    htmlDoc = doc["document"]
    inputStr = doc["input"]
    res = StudentsControler(htmlDoc,inputStr).run()
    return res

@app.post("/download/all")
def download_all(doc: dict):
    htmlDoc = doc["document"]
    all_df = generate_all_df(htmlDoc)
    # 临时文件的保存目录
    if not os.path.isdir("temp"):
        os.mkdir("temp")

    # 获取班级信息和作业信息
    soup = BeautifulSoup(htmlDoc, "html.parser")
    options = soup.find_all("option")
    class_homework_info = "python"
    for option in options:
        if option.has_attr("selected"):
            class_homework_info += "-" + option.text

    #添加时间戳后缀防止文件名重复, 文件不能有冒号所以要换掉
    temp_file_path = "./temp/{}.xlsx".format(class_homework_info+str(datetime.datetime.now()).replace(":", "-"))
    all_df.to_excel(temp_file_path, index=False)
    res = FileResponse(temp_file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",filename="{}.xlsx".format(class_homework_info))
    res.headers["responseType"] = "blob"
    return res

@app.post("/download/redo")
def download_redo(doc: dict):
    htmlDoc = doc["document"]
    all_df = generate_all_df(htmlDoc)
    # 临时文件的保存目录
    if not os.path.isdir("temp"):
        os.mkdir("temp")

    # 获取班级信息和作业信息
    soup = BeautifulSoup(htmlDoc, "html.parser")
    options = soup.find_all("option")
    class_homework_info = "python"
    for option in options:
        if option.has_attr("selected"):
            class_homework_info += "-" + option.text
    redo_df = all_df
    # 如果没有成绩列的话，可能发送的页面数据是汇总的数据表, 那么直接返回原始表
    if "成绩" in all_df.columns:
        redo_df = all_df[all_df["成绩"]<70]

    #添加时间戳后缀防止文件名重复, 文件不能有冒号所以要换掉
    temp_file_path = "./temp/{}-重做.xlsx".format(class_homework_info+str(datetime.datetime.now()).replace(":", "-"))
    redo_df.to_excel(temp_file_path, index=False)
    res = FileResponse(temp_file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",filename="{}-重做.xlsx".format(class_homework_info))
    res.headers["responseType"] = "blob"
    return res

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)