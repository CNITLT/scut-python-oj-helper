from concurrent.futures import ThreadPoolExecutor
from typing import Union
from pydantic import BaseModel

from Question import Question
from Student import Student

from fastapi import FastAPI

from multiprocessing import cpu_count

import uvicorn

from StudentsControler import StudentsControler

app = FastAPI()


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

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)