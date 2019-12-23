import json
from time import sleep
from os.path import join

class CodeRunTests:
    def __init__(self,problem_id):
        self.problem_id=problem_id

    def pythonData(self):
        code1="a=map(int,input().split())\nb=map(int,input().split())\nprint(list(map(lambda x:sum(x), zip(a,b))))"
        code2="n = int(input())\nfor i in range(n):\n\tprint(int(input()) + int(input()))"
        data=dict(
            prblmid=self.problem_id,
            userid="wkgs426haqie6yvnacswteelkjsndteaqp",
            codecontent=code2,
            lang="py",
            stype = "sample"
        )
        return data

    def golangData(self):
        with open(join("testcasefile/test.go")) as f:
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
        with open(join("testcasefile/test.java")) as f:
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
        with open(join("testcasefile/test.c")) as f:
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
