import json
from time import sleep
from os.path import join
from platform import system

class CodeRunTests:
    def __init__(self,problem_id,user_id,contestid="",ctype=""):
        self.problem_id=problem_id
        self.user_id=user_id
        self.contestid = contestid
        self.ctype = ctype

    def pythonData(self,testtimeout=False):
        timeoutfile =lambda : "testtimeout.py" if testtimeout else "test.py"
        path = "testcasefile/"+timeoutfile()
        if system()=='Windows':
            path = "C:/Users/Harjacober/Desktop/PythonProjects/Contest-Platform/testcasefile/"+timeoutfile()
       
        with open(path) as f:
            code = f.read()
        data=dict(
            prblmid=self.problem_id,
            userid=self.user_id,
            codecontent=code,
            lang="py",
            stype = "test",
            contestid = self.contestid,
            ctype = self.ctype
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
            userid=self.user_id,
            codecontent=code,
            lang="go",
            stype = "test",
            contestid = self.contestid,
            ctype = self.ctype
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
            userid=self.user_id,
            codecontent=code,
            lang="java",
            stype = "test",
            contestid = self.contestid,
            ctype = self.ctype
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
            userid=self.user_id,
            codecontent=code,
            lang="c",
            stype = "test",
            contestid = self.contestid,
            ctype = self.ctype
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

    def run(self,url,apiKey,appClient,requestData):

        header={"Authorization":"Bearer "+apiKey}
        
        resp=appClient.post(url,data=requestData,headers=header)
        print(resp.data.decode())
        resp=json.loads(resp.data.decode())["data"][0]

        task_id=resp["_id"]
      
        data=dict(
            prblmid=self.problem_id,
            userid=self.user_id,
            taskid=task_id,
            lang="py",
            stype = "test"
        )

        sleep(3) # wait some second for result

        resp=appClient.post("/run/code/status/",data=data,headers=header)

        return resp
