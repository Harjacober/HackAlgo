import unittest
import json
import os,io

from pymongo import MongoClient
from app import  *
from db.models import *
from coderun import CodeRunTests 
from datetime import datetime

app_client=app.test_client()

#On furst run, Run create.py first before this test file
langs=['go', 'py', 'java', 'c', 'c++', 'python', 'python2', 'php', 'js']

class AppTests(unittest.TestCase):
    api_token=""
    problem_id=""
    contest_type=""
    contest_id = ""
    @classmethod
    def setToken(cls,api_token):
        cls.api_token= api_token

    @classmethod
    def setProblemID(cls,problem_id):
        cls.problem_id=problem_id

    @classmethod
    def setContestIdandType(cls,contest_type, contest_id):
        cls.contest_type = contest_type
        cls.contest_id = contest_id    

    def test_folder_avail(self): 
        for lgn in langs:
            directory = os.path.dirname("/tmp/{}".format(lgn))
            os.stat(directory)

    def getValidTime(self):
        return datetime.now().timestamp() + 13*60*60*1000.0        

    def reg_test(self,url):
        resp=app_client.post(url, data=dict(
            username="marlians",
            pswd="aburunakamaki"
        )) 
        self.assertTrue('blank' in resp.data.decode())

        resp=app_client.post(url, data=dict(
            username="marlians",
            pswd="aburunakamaki",
            email="nairamarley@yahoo.com"
        ))

        resp=json.loads(resp.data.decode())

        self.assertTrue(len(resp["access_token"])>0)

        self.api_token=resp["access_token"]
        AppTests.setToken(self.api_token)

        resp=app_client.post(url, data=dict(
            username="marlians",
            pswd="aburunakamaki",
            email="nairamarley@yahoo.com"
        ))

        self.assertTrue("taken" in resp.data.decode())

    def login_test(self,url):
        print(url)
        resp=app_client.post(url, data=dict(
            username="marlians",
            pswd="aburunakamaki"
        ))

        self.assertTrue('login successfuly' in resp.data.decode())

        resp=app_client.post(url, data=dict(
            username="marlians",
            pswd="aburunakamakif"
        ))

        self.assertTrue('check the username and password' in resp.data.decode())

        
       
    def test_admin_reg(self):
        self.reg_test("/admin/registration/")
        self.login_test("/admin/login/")

    def test_user_reg(self):
        self.reg_test("/user/registration/")
        self.login_test("/user/login/")


    def test_problem_add(self):
       
        self.assertTrue(len(self.api_token)>0)

        # Authorization: Bearer <token>
        header={"Authorization":"Bearer "+self.api_token}
        c1 = "1 2 3 4 5\n2 3 5 6 7,3 4 8 9 1\n4 2 3 5 1,5 2 4 3 1\n6 3 5 7 8"
        a1 = "[3, 5, 8, 10, 12],[7, 6, 11, 14, 2],[11, 5, 9, 10, 9]"
        s1 = "3 4 6 3\n2 4 6 2"
        as1= "[5, 8, 12, 5]"
        c2 = b"3\r\n1\r\n2\r\n3\r\n4\r\n5\r\n6,2\r\n7\r\n8\r\n9\r\n10,1\r\n9\r\n10'"
        a2= b"3\n7\n11,\n15\n19,\n19"
        s2 = b"2\n3\n4\n2\n1"
        as2 = b"7\n3"
        data=dict(
            name="problem test",
            author="marlians",
            testcases=(io.BytesIO(c2), 'test.in'),
            sizeoftestcases="3",
            answercases=(io.BytesIO(a2), 'anstest.in'),
            samplecases=(io.BytesIO(s2), 'sampletest.in'),
            sizeofsamplecases="1",
            sampleanswercases = (io.BytesIO(as2), 'answersampletest.in'), 
            problemstatement="Read the input and print them",
            category="test",
            timelimit=1,
            memorylimit=250
        )

        resp=app_client.post("/add/problem/",data=data,headers=header,content_type='multipart/form-data')
        
        self.assertTrue("New Problem Added" in resp.data.decode())

        resp=json.loads(resp.data.decode())

        problem_id=resp["data"]["prblmid"]

        self.setProblemID(problem_id)

        data=dict(
            prblmid=problem_id
        )

        resp=app_client.post("/get/problem/",data=data,headers=header)

        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("author" in resp.data.decode())
        self.assertTrue("sizeoftestcases" in resp.data.decode())
        self.assertTrue("samplecases" in resp.data.decode())

        resp=app_client.get("/get/problem/?prblmid="+problem_id,headers=header)


        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("author" in resp.data.decode())
        self.assertTrue("sizeoftestcases" in resp.data.decode())
        self.assertTrue("samplecases" in resp.data.decode())


    def test_contest_create(self):
       
        self.assertTrue(len(self.api_token)>0)

        # Authorization: Bearer <token>
        header={"Authorization":"Bearer "+self.api_token} 
        data=dict(
            title="Educational Contest",
            creator="marlians", 
            contesttype="TYPEA",
            desc=""
        )

        resp=app_client.post("/contest/initialize/", data=data, headers=header, content_type='multipart/form-data')

        self.assertTrue("Contest Created Successfully" in resp.data.decode())
        
        resp=json.loads(resp.data.decode())

        contest_id=resp["data"]["contestid"]
        contest_type = resp["data"]["contesttype"]

        self.setContestIdandType(contest_type, contest_id)

        data=dict(
            title = "Educational Contest", 
            desc = "Description goes here",
            duration = 120*60*60*1000.0,
            starttime = self.getValidTime(),
            authorusername = "marlians",
            contestid = contest_id

        )
        resp=app_client.post("/contest/{}/update/".format(contest_type), data=data, headers=header)

        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("Update Successful" in resp.data.decode()) 


        c1 = "1 2 3 4 5\n2 3 5 6 7,3 4 8 9 1\n4 2 3 5 1,5 2 4 3 1\n6 3 5 7 8"
        a1 = "[3, 5, 8, 10, 12],[7, 6, 11, 14, 2],[11, 5, 9, 10, 9]"
        s1 = "3 4 6 3\n2 4 6 2"
        as1= "[5, 8, 12, 5]"
        c2 = b"3\r\n1\r\n2\r\n3\r\n4\r\n5\r\n6,2\r\n7\r\n8\r\n9\r\n10,1\r\n9\r\n10'"
        a2= b"3\n7\n11,\n15\n19,\n19"
        s2 = b"2\n3\n4\n2\n1"
        as2 = b"7\n3"
        data=dict(
            authorusername = "marlians",
            name="problem test", 
            testcases=(io.BytesIO(c2), 'test.in'),
            sizeoftestcases="3",
            answercases=(io.BytesIO(a2), 'anstest.in'),
            samplecases=(io.BytesIO(s2), 'sampletest.in'),
            sizeofsamplecases="1",
            sampleanswercases = (io.BytesIO(as2), 'answersampletest.in'), 
            problemstatement="Read the input and print them",
            contestid = contest_id,
            timelimit=1000,
            memorylimit=1024,
            prblmscore=900
        )
        resp=app_client.post("/contest/{}/problem/add/".format(contest_type), data=data,headers=header,content_type='multipart/form-data')
 
        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("contestid" in resp.data.decode())
        self.assertTrue("prblmid" in resp.data.decode())  


    def test_run_code(self):
        self.assertTrue(len(self.problem_id)>0)

        codeRun=CodeRunTests(self.problem_id)

        #testing python
        resp=codeRun.run(self.api_token,app_client,codeRun.pythonData())
        data=json.loads(resp.data.decode())
        self.assertTrue(data["data"][0]["result"][0]["passed"])

        #testingtimeout py code
        resp=codeRun.run(self.api_token,app_client,codeRun.pythonData(testtimeout=True))
        data=json.loads(resp.data.decode())
        self.assertTrue(data["data"][0]["result"][0]["passed"]==False)
        
        #testing golang
        resp=codeRun.run(self.api_token,app_client,codeRun.golangData())
        data=json.loads(resp.data.decode())
        if not data["data"][0]["result"][0]["passed"]:
            print(data["data"][0]["result"][0]["errput"])
        self.assertTrue(data["data"][0]["result"][0]["passed"])

        #rtesting c
        resp=codeRun.run(self.api_token,app_client,codeRun.cData())
        data=json.loads(resp.data.decode())
        if not data["data"][0]["result"][0]["passed"]:
            print(data["data"][0]["result"][0]["errput"])
        self.assertTrue(data["data"][0]["result"][0]["passed"])

         #rtesting timeout c
        resp=codeRun.run(self.api_token,app_client,codeRun.cData(testtimeout=True))
        data=json.loads(resp.data.decode())
        self.assertTrue(data["data"][0]["result"][0]["passed"]==False)

        #testing java
        resp=codeRun.run(self.api_token,app_client,codeRun.javaData())
        data=json.loads(resp.data.decode())
        if not data["data"][0]["result"][0]["passed"]:
            print(data["data"][0]["result"][0]["errput"])
        self.assertTrue(data["data"][0]["result"][0]["passed"])

        #testing java timeout
        resp=codeRun.run(self.api_token,app_client,codeRun.javaData(testtimeout=True))
        data=json.loads(resp.data.decode())
        self.assertTrue(data["data"][0]["result"][0]["passed"]==False)

if __name__ == "__main__":
    unittest.main()