import json
from time import sleep
from os.path import join
from platform import system

class CodeRunTests:
    def __init__(self,problem_id):
        self.problem_id=problem_id

    def pythonData(self,testtimeout=False):
        timeoutfile =lambda : "testtimeout.py" if testtimeout else "test.py"
        path = "testcasefile/"+timeoutfile()
        if system()=='Windows':
            path = "C:/Users/Harjacober/Desktop/PythonProjects/Contest-Platform/testcasefile/"+timeoutfile()
       
        with open(path) as f:
            code = f.read()
        data=dict(
            prblmid=self.problem_id,
            userid="wkgs426haqie6yvnacswteelkjsndteaqp",
            codecontent=code,
            lang="py",
            stype = "sample"
        )
        return data


    def golangData(self):
        path = "testcasefile/test.go"
        if system()=='Windows':
            path = "C:/Users/Harjacober/Desktop/PythonProjects/Contest-Platform/testcasefile/test.go"

        with open(path) as f:
            code=f.read()
        data=dict(
            prblmid=self.problem_id,
            userid="wkgs426haqie6yvnacswteelkjsndteaqp",
            codecontent=code,
            lang="go",
            stype = "sample"
        )
        return data

    def javaData(self,testtimeout=False):
        timeoutfile =lambda : "testtimeout.java" if testtimeout else "test.java"
        path = "testcasefile/"+timeoutfile()
        if system()=='Windows':
            path = "C:/Users/Harjacober/Desktop/PythonProjects/Contest-Platform/testcasefile/"+timeoutfile()
        with open(path) as f:
            code=f.read()
        data=dict(
            prblmid=self.problem_id,
            userid="wkgs426haqie6yvnacswteelkjsndteaqp",
            codecontent=code,
            lang="java",
            stype = "sample"
        )
        return data


    def cData(self,testtimeout=False):
        timeoutfile =lambda : "testtimeout.c" if testtimeout else "test.c"
        path = "testcasefile/"+timeoutfile()
        if system()=='Windows':
            path = "C:/Users/Harjacober/Desktop/PythonProjects/Contest-Platform/testcasefile/"+timeoutfile()
        with open(path) as f:
            code=f.read()
        data=dict(
            prblmid=self.problem_id,
            userid="wkgs426haqie6yvnacswteelkjsndteaqp",
            codecontent=code,
            lang="c",
            stype = "sample"
        )
        return data

    def cplusplusData(self):
        return {}

    def jsData(self):
        return {

        }
    def phpData(self):
        return {

        }

    def run(self,apiKey,appClient,requestData):

        header={"Authorization":"Bearer "+apiKey}
        
        resp=appClient.post("/run/code/",data=requestData,headers=header)

        resp=json.loads(resp.data.decode())["data"][0]

        task_id=resp["_id"]
      
        data=dict(
            prblmid=self.problem_id,
            userid="wkgs426haqie6yvnacswteelkjsndteaqp",
            taskid=task_id,
            lang="py",
            stype = "test"
        )

        sleep(3) # wait some second for result

        resp=appClient.post("/run/code/status/",data=data,headers=header)

        return resp
