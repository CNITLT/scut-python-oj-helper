import os.path
import re
from bs4 import BeautifulSoup
import subprocess
class Question:
    @staticmethod
    def getQuestion(htmlDoc:str):
        soup = BeautifulSoup(htmlDoc, "html.parser")
        return soup.find_all("div", "autoBR")[0].text




