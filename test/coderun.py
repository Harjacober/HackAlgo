import json
from time import sleep
from os.path import join

class CodeRunTests:
    def __init__(self,problem_id):
        self.problem_id=problem_id

    def pythonData(self):
        win_path = "C:/Users/Harjacober/Desktop/PythonProjects/Contest-Platform/testcasefile/test.py"
        path = "testcasefile/test.py"
        with open(win_path) as f:
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
        win_path = "C:/Users/Harjacober/Desktop/PythonProjects/Contest-Platform/testcasefile/test.go"
        path = "testcasefile/test.go"
        with open(win_path) as f:
            code=f.read()
        data=dict(
            prblmid=self.problem_id,
            userid="wkgs426haqie6yvnacswteelkjsndteaqp",
            codecontent=code,
            lang="go",
            stype = "sample"
        )
        return data

    def javaData(self):
        win_path = "C:/Users/Harjacober/Desktop/PythonProjects/Contest-Platform/testcasefile/test.java"
        path = "testcasefile/test.java"
        with open(win_path) as f:
            code=f.read()
        data=dict(
            prblmid=self.problem_id,
            userid="wkgs426haqie6yvnacswteelkjsndteaqp",
            codecontent=code,
            lang="java",
            stype = "sample"
        )
        return data


    def cData(self):
        win_path = "C:/Users/Harjacober/Desktop/PythonProjects/Contest-Platform/testcasefile/test.c"
        path = "testcasefile/test.c"
        with open(win_path) as f:
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

        sleep(3) # wait a second for result

        resp=appClient.post("/run/code/status/",data=data,headers=header)

        return resp
