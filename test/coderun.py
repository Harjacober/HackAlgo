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

    def testMemory(self):
        path = "testcasefile/memoryconsuption.py"
       
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

    def run(self,url,url_status,apiKey,appClient,requestData):

        header={"Authorization":"Bearer "+apiKey}
        
        resp=appClient.post(url,data=requestData,headers=header)
        
        resp=json.loads(resp.data.decode())["data"][0]

        task_id=resp["_id"]
      
        data=dict(
            prblmid=self.problem_id,
            userid=self.user_id,
            taskid=task_id,
            lang=resp["lang"],
            stype = "test",
            contestid = self.contestid,
            contesttype = self.ctype
        )
        sleepseconds=5 if resp["lang"]=='java' else 3
        sleep(sleepseconds) # wait some second for result

        resp=appClient.post(url_status,data=data,headers=header)

        return resp
